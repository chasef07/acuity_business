---
name: abita-amd-dev-curl
description: "Direct curl workflow for Abita AdvancedMD dev XMLRPC checks. Use when Chase asks to hit dev AMD directly, test addpatient/lookuppatient/getdemographic payloads outside middleware, verify phone formatting such as no +1 country code, or compare AMD provider behavior against abita_middleware code."
---

# Abita AMD Dev Curl

Use direct `curl` only for dev AMD probes and only when live provider behavior matters.
Keep tokens, cookies, provider responses, and any non-dev credentials out of command lines, logs, PRs, and final answers.

## Boundaries

- Default to AMD dev. Do not run against prod unless Chase explicitly says so.
- Treat `addpatient`, `addinsurance`, and appointment writes as live mutations, even in dev.
- Use fake patients only, with obvious names like `PHONETEST<timestamp>,CODEX`.
- Never print passwords, tokens, cookies, raw credentials, or full provider responses.
- Report sanitized facts: action, success/failure, fake patient id/name, submitted test phone, and lookup match.
- Re-check `/Users/chasefagen/abita_middleware` before claiming current middleware behavior.

## Dev Credentials

Read dev credentials from local environment or the local-only env file. Do not
commit credentials into this skill, shell history, logs, PRs, or final answers.

Default local env file:

```text
/Users/chasefagen/.config/agent-scripts/abita-amd-dev.env
```

Required environment variables:

```bash
ADVANCEDMD_USERNAME
ADVANCEDMD_PASSWORD
ADVANCEDMD_OFFICE_KEY
ADVANCEDMD_APP_NAME
AMD_ENV=dev
```

## Auth Shape

AdvancedMD uses the middleware's two-step login:

1. POST XML login to:
   `https://partnerlogin.advancedmd.com/practicemanager/xmlrpc/processrequest.aspx`
2. Extract `usercontext@webserver`.
3. POST the same XML login to:
   `<webserver>/xmlrpc/processrequest.aspx`
4. Extract the session token from `<usercontext>`.
5. POST XMLRPC JSON to:
   `<webserver>/xmlrpc/processrequest.aspx`
   with headers:
   - `Cookie: token=<token>`
   - `Content-Type: application/json`
   - `Accept: application/json`

## Dev Phone Probe

Use this when testing whether AMD dev accepts a patient phone without `+1`.
It creates one fake dev patient with `@homephone` set to `(727)555-0199`, then verifies that `lookuppatient` finds that patient by `7275550199`.

Known-good result from 2026-06-26: dev AMD accepted `@homephone: "(727)555-0199"` and a 10-digit `lookuppatient` contained the created patient.

Run with `bash`. If env vars are missing, the script prompts with hidden input.

```bash
set +x

cred_file="${ABITA_AMD_DEV_ENV:-/Users/chasefagen/.config/agent-scripts/abita-amd-dev.env}"
if [ -f "$cred_file" ]; then
  set -a
  # shellcheck disable=SC1090
  . "$cred_file"
  set +a
fi

: "${AMD_ENV:=dev}"
export ADVANCEDMD_USERNAME ADVANCEDMD_PASSWORD ADVANCEDMD_OFFICE_KEY ADVANCEDMD_APP_NAME AMD_ENV

for key in ADVANCEDMD_USERNAME ADVANCEDMD_PASSWORD ADVANCEDMD_OFFICE_KEY ADVANCEDMD_APP_NAME; do
  if [ -z "${!key:-}" ]; then
    read -r -s -p "$key: " "$key"
    echo
    export "$key"
  fi
done

msgtime=$(date "+%m/%d/%Y %I:%M:%S %p")
login_xml=$(printf '<ppmdmsg action="login" class="login" msgtime="%s" username="%s" psw="%s" officecode="%s" appname="%s"/>' \
  "$msgtime" \
  "$ADVANCEDMD_USERNAME" \
  "$ADVANCEDMD_PASSWORD" \
  "$ADVANCEDMD_OFFICE_KEY" \
  "$ADVANCEDMD_APP_NAME")

web_resp=$(curl -fsS \
  -H "Content-Type: application/xml" \
  --data "$login_xml" \
  "https://partnerlogin.advancedmd.com/practicemanager/xmlrpc/processrequest.aspx")

webserver=$(printf "%s" "$web_resp" | perl -0ne 'print $1 if /webserver="([^"]+)"/')
if [ -z "$webserver" ]; then
  echo "login_step_1=failed_no_webserver"
  exit 1
fi

token_resp=$(curl -fsS \
  -H "Content-Type: application/xml" \
  --data "$login_xml" \
  "$webserver/xmlrpc/processrequest.aspx")

token=$(printf "%s" "$token_resp" | perl -0ne 'print $1 if /<usercontext[^>]*>([^<]+)<\/usercontext>/')
if [ -z "$token" ]; then
  echo "login_step_2=failed_no_token"
  exit 1
fi

stamp=$(date "+%m%d%H%M%S")
last="PHONETEST$stamp"
first="CODEX"
phone="(727)555-0199"
phone_digits="7275550199"
xmlrpc_url="${webserver%/}/xmlrpc/processrequest.aspx"

add_payload=$(jq -n \
  --arg msgtime "$msgtime" \
  --arg name "$last,$first" \
  --arg phone "$phone" \
  --arg email "codex-phone-test@example.invalid" \
  '{
    ppmdmsg: {
      "@action": "addpatient",
      "@class": "api",
      "@msgtime": $msgtime,
      "@nocookie": "0",
      patientlist: {
        patient: {
          "@respparty": "SELF",
          "@name": $name,
          "@sex": "U",
          "@relationship": "1",
          "@hipaarelationship": "18",
          "@dob": "01/01/1990",
          "@ssn": "",
          "@chart": "AUTO",
          "@profile": "1135",
          address: {
            "@address1": "",
            "@address2": "123 Dev Test St",
            "@city": "Spring Hill",
            "@state": "FL",
            "@zip": "34606"
          },
          contactinfo: {
            "@homephone": $phone,
            "@email": $email
          }
        }
      }
    }
  }')

add_resp=$(curl -fsS \
  -H "Cookie: token=$token" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json" \
  --data "$add_payload" \
  "$xmlrpc_url")

add_error=$(printf "%s" "$add_resp" | jq -r '.PPMDResults.Error // .PPMDResults.Results.Error // empty' 2>/dev/null)
if [ -n "$add_error" ]; then
  echo "addpatient=amd_error"
  printf "%s\n" "$add_resp" | jq -r '.PPMDResults.Error, .PPMDResults.Results.Error | select(.)'
  exit 2
fi

patient_id=$(printf "%s" "$add_resp" | jq -r '.PPMDResults.Results.patientlist.patient["@id"] // empty')
patient_name=$(printf "%s" "$add_resp" | jq -r '.PPMDResults.Results.patientlist.patient["@name"] // empty')
if [ -z "$patient_id" ]; then
  echo "addpatient=unexpected_response"
  exit 3
fi

lookup_payload=$(jq -n \
  --arg msgtime "$msgtime" \
  --arg phone "$phone_digits" \
  '{ppmdmsg: {"@action": "lookuppatient", "@class": "api", "@msgtime": $msgtime, "@nocookie": "0", "@phone": $phone}}')

lookup_resp=$(curl -fsS \
  -H "Cookie: token=$token" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json" \
  --data "$lookup_payload" \
  "$xmlrpc_url")

contains=$(printf "%s" "$lookup_resp" | jq -r --arg id "$patient_id" '[.PPMDResults.Results.patientlist.patient] | flatten | map(select(.["@id"] == $id)) | length > 0')
itemcount=$(printf "%s" "$lookup_resp" | jq -r '.PPMDResults.Results.patientlist["@itemcount"] // ([.PPMDResults.Results.patientlist.patient] | flatten | length)')

echo "login=ok"
echo "addpatient=ok"
echo "patient_id=$patient_id"
echo "patient_name=$patient_name"
echo "sent_homephone=$phone"
echo "lookup_10_digit_itemcount=$itemcount"
echo "lookup_contains_created_patient=$contains"
```

## Interpreting Results

- `addpatient=ok` means AMD accepted the phone value in the dev patient write.
- `lookup_contains_created_patient=true` means the stored patient can be found by a 10-digit phone lookup.
- If this passes but reminders still fail, inspect whether reminders depend on `@cellphone` or `@mobilephone`; current middleware evidence may show only `@homephone` being written.
- If curl passes but middleware fails, inspect the formatting boundary in `domain.FormatPhone`, then the `HandleAddPatient` call into `clients.AddPatientParams.Phone`.

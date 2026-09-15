# 📞 Inbound Phone & SIP Setup Guide (Free & Production Routes)

This guide shows how to connect an inbound phone line to the **Pinnacle AI Voice Receptionist** (Sarah at High Springs Pediatrics).

---

## Route 1: 100% Free Testing via SIP Softphone (Linphone / MicroSIP)

If you don't want to spend anything on telecom carriers for initial validation, use internet-to-internet SIP:

1. **Get a Free SIP Account**:
   - Register a free account at [Linphone.org](https://www.linphone.org/free-sip-service) or [SIP2SIP.info](https://sip2sip.info/).
   - You will receive a SIP address, such as: sip:pinnacle-clinic@sip.linphone.org.
2. **Download a Free Softphone Client**:
   - Download **Linphone** (Desktop/iOS/Android) or **MicroSIP** (Windows).
3. **Configure & Test**:
   - Log into the softphone app with your test credentials.
   - When you call your SIP address from your PC or mobile app, the call routes directly into your local voice server or Tel-Agent SIP listener.

---

## Route 2: Free US Phone Number via Twilio Free Trial

To test real telephone dialing from ordinary cell phones and landlines:

1. **Sign Up**: Create an account on [Twilio](https://www.twilio.com). The free trial grants you ~ in free credits.
2. **Pick a Phone Number**: Claim a free US phone number (e.g. +1 (386) ... for Florida).
3. **Configure Voice Webhook**:
   - Go to **Phone Numbers** -> **Manage** -> **Active Numbers** -> Click your number.
   - Under **Voice Configuration**:
     - *A Call Comes In*: Select **Webhook**.
     - *URL*: Enter your server endpoint (use 
grok http 8000 or Cloudflare Tunnel if running locally):
       `
       https://<your-tunnel-url>/api/telephony/twilio/inbound
       `
     - *HTTP Method*: POST.
4. **Dial**: Call your Twilio number from your mobile phone. Sarah greets you immediately and handles appointment booking, refills, and queries.

---

## Route 3: Production DID (/mo via Telnyx or SIP.US)

For permanent clinic deployment without per-minute SaaS markups:

1. **Get a Number**: On [Telnyx](https://telnyx.com), search for a local Florida DID number (costs ~.00/month, ~.005/min).
2. **Create SIP Connection**:
   - Create a **SIP Trunk / Connection** on Telnyx.
   - Set the destination to your server's SIP URI or public IP address.
3. **Zero Markup**: Bypasses all middleman platform fees (like Vapi's .05+/min markup). Audio streams directly to your self-hosted Tel-Agent stack.

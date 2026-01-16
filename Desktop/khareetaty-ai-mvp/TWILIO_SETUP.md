# 📱 Twilio Setup Guide for Khareetaty AI

## Overview

This guide walks you through setting up Twilio for WhatsApp and SMS alerts in the Khareetaty AI platform.

---

## 🎯 What You'll Need

1. **Twilio Account** (Free trial available)
2. **WhatsApp Business API Access** (via Twilio)
3. **Phone number** for receiving alerts
4. **5-10 minutes** for setup

---

## 📋 Step 1: Create Twilio Account

### 1.1 Sign Up

1. Go to [https://www.twilio.com/try-twilio](https://www.twilio.com/try-twilio)
2. Fill in your details:
   - Email: `bader.naser.ai.sa@gmail.com`
   - Password: (create a secure password)
   - First Name: Bader
   - Last Name: Naser
3. Verify your email address
4. Verify your phone number: `+96566338736`

### 1.2 Get Your Credentials

Once logged in:

1. Go to **Console Dashboard**
2. Find your credentials:
   - **Account SID**: `ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`
   - **Auth Token**: Click "Show" to reveal
3. **Copy these values** - you'll need them for `.env` file

---

## 📱 Step 2: Set Up WhatsApp Messaging

### 2.1 Enable WhatsApp Sandbox (For Testing)

1. In Twilio Console, go to **Messaging** → **Try it out** → **Send a WhatsApp message**
2. You'll see a sandbox number like: `whatsapp:+14155238886`
3. **Join the sandbox:**
   - Open WhatsApp on your phone
   - Send a message to `+1 415 523 8886`
   - Message content: `join <your-sandbox-code>`
   - Example: `join happy-tiger`
4. You'll receive a confirmation message

### 2.2 Production WhatsApp Setup (Optional)

For production deployment:

1. Go to **Messaging** → **WhatsApp** → **Senders**
2. Click **Request to enable your Twilio number for WhatsApp**
3. Follow Facebook Business verification process
4. This takes 1-2 weeks for approval

**For MVP/Testing:** Use the sandbox (Step 2.1)

---

## 📞 Step 3: Set Up SMS Messaging

### 3.1 Get a Twilio Phone Number

1. Go to **Phone Numbers** → **Manage** → **Buy a number**
2. Select country: **Kuwait** or **United States**
3. Check capabilities:
   - ✅ SMS
   - ✅ MMS (optional)
4. Click **Buy** (uses trial credit)
5. Your number: `+1XXXXXXXXXX`

### 3.2 Configure SMS Settings

1. Go to your purchased number
2. Under **Messaging**:
   - Configure webhook URLs (optional for now)
   - Enable SMS capabilities
3. Save configuration

---

## ⚙️ Step 4: Configure Khareetaty AI

### 4.1 Update .env File

Open `/Users/bdr.ai/Desktop/khareetaty-ai-mvp/.env` and update:

```bash
# Twilio Configuration
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=your_auth_token_here
TWILIO_PHONE_NUMBER=+1XXXXXXXXXX
WHATSAPP_SENDER=whatsapp:+14155238886

# Alert Recipients
ALERT_PHONE_NUMBER=+96566338736
ALERT_WHATSAPP_NUMBER=whatsapp:+96566338736
```

### 4.2 Replace Placeholder Values

1. **TWILIO_ACCOUNT_SID**: Your Account SID from Twilio Console
2. **TWILIO_AUTH_TOKEN**: Your Auth Token from Twilio Console
3. **TWILIO_PHONE_NUMBER**: Your purchased Twilio number
4. **WHATSAPP_SENDER**: Sandbox number (or production number)
5. **ALERT_PHONE_NUMBER**: Your Kuwait mobile number
6. **ALERT_WHATSAPP_NUMBER**: Same number with `whatsapp:` prefix

---

## 🧪 Step 5: Test Your Configuration

### 5.1 Test WhatsApp Alert

```bash
cd /Users/bdr.ai/Desktop/khareetaty-ai-mvp
python3 -c "
from services.notifications import send_whatsapp
send_whatsapp('+96566338736', '🚨 Test alert from Khareetaty AI')
print('WhatsApp test sent!')
"
```

**Expected Result:**
- You receive a WhatsApp message on your phone
- Message: "🚨 Test alert from Khareetaty AI"

### 5.2 Test SMS Alert

```bash
python3 -c "
from services.notifications import send_sms
send_sms('+96566338736', '🚨 Test SMS from Khareetaty AI')
print('SMS test sent!')
"
```

**Expected Result:**
- You receive an SMS on your phone
- Message: "🚨 Test SMS from Khareetaty AI"

### 5.3 Test Email Alert

```bash
python3 -c "
from services.notifications import send_email
send_email('bader.naser.ai.sa@gmail.com', 'Test Alert', '🚨 Test email from Khareetaty AI')
print('Email test sent!')
"
```

---

## 🔧 Step 6: Test Full Alert Pipeline

### 6.1 Trigger Test Alert

```bash
cd /Users/bdr.ai/Desktop/khareetaty-ai-mvp
python3 automation/trigger_alerts.py
```

**What This Does:**
1. Queries zones_hotspots for high-risk areas
2. Checks if score > threshold (10)
3. Sends alerts to all active analysts and superadmins
4. Logs alerts to alerts_log table

### 6.2 Verify Alert Logs

```bash
psql -U bdr.ai -d khareetaty_ai -c "SELECT * FROM alerts_log ORDER BY created_at DESC LIMIT 5;"
```

---

## 💰 Twilio Pricing (As of 2026)

### Free Trial
- **$15.50 credit** upon signup
- Enough for ~500 SMS or ~1000 WhatsApp messages
- Perfect for MVP testing

### Production Pricing
- **WhatsApp**: $0.005 per message (Kuwait)
- **SMS**: $0.03-0.05 per message (Kuwait)
- **Phone Number**: $1/month

### Estimated Costs for Khareetaty AI

Assuming:
- 10 alerts per day
- 5 recipients per alert
- 50 messages/day

**Monthly Cost:**
- WhatsApp: 50 × 30 × $0.005 = **$7.50/month**
- SMS: 50 × 30 × $0.04 = **$60/month**
- Phone Number: **$1/month**

**Total: ~$8-70/month** (depending on channel)

**Recommendation:** Use WhatsApp for cost efficiency

---

## 🚨 Troubleshooting

### Issue 1: "Authentication Error"

**Cause:** Wrong Account SID or Auth Token

**Solution:**
1. Double-check credentials in Twilio Console
2. Ensure no extra spaces in `.env` file
3. Restart backend server after updating `.env`

### Issue 2: "Unverified Number"

**Cause:** Trial account can only send to verified numbers

**Solution:**
1. Go to **Phone Numbers** → **Verified Caller IDs**
2. Add `+96566338736`
3. Verify via SMS code

### Issue 3: WhatsApp Not Received

**Cause:** Not joined sandbox or wrong number format

**Solution:**
1. Ensure you joined sandbox: Send `join <code>` to sandbox number
2. Check number format: `whatsapp:+96566338736` (no spaces)
3. Verify sandbox is active in Twilio Console

### Issue 4: "Module Not Found: twilio"

**Cause:** Twilio package not installed

**Solution:**
```bash
pip3 install twilio --break-system-packages
```

---

## 🔐 Security Best Practices

### 1. Protect Your Credentials

- ❌ **Never commit** `.env` file to Git
- ✅ **Use** `.env.example` for templates
- ✅ **Rotate** Auth Token every 90 days

### 2. Use Environment Variables

```python
# ✅ Good
account_sid = os.getenv("TWILIO_ACCOUNT_SID")

# ❌ Bad
account_sid = "ACxxxxxxxxxxxxxxxx"  # Hardcoded!
```

### 3. Implement Rate Limiting

```python
# Prevent alert spam
if last_alert_time and (datetime.now() - last_alert_time).seconds < 300:
    print("Rate limit: Wait 5 minutes between alerts")
    return
```

### 4. Monitor Usage

1. Set up **Usage Triggers** in Twilio Console
2. Alert when spending exceeds $50/month
3. Review logs weekly

---

## 📊 Step 7: Monitor Twilio Usage

### 7.1 Twilio Console Dashboard

1. Go to **Monitor** → **Logs** → **Messages**
2. View:
   - Sent messages
   - Delivery status
   - Error messages
   - Cost per message

### 7.2 Set Up Usage Alerts

1. Go to **Account** → **Usage Triggers**
2. Create trigger:
   - **Trigger Type**: Total Usage
   - **Threshold**: $50
   - **Notification**: Email to `bader.naser.ai.sa@gmail.com`
3. Save trigger

---

## ✅ Configuration Checklist

- [ ] Twilio account created
- [ ] Account SID and Auth Token obtained
- [ ] WhatsApp sandbox joined
- [ ] Twilio phone number purchased
- [ ] `.env` file updated with credentials
- [ ] WhatsApp test message sent successfully
- [ ] SMS test message sent successfully
- [ ] Email test sent successfully
- [ ] Full alert pipeline tested
- [ ] Usage triggers configured
- [ ] Credentials secured (not in Git)

---

## 🎯 Next Steps

Once Twilio is configured:

1. ✅ **Test alerts** with real hotspot data
2. ✅ **Configure** alert thresholds in `config/escalation.yaml`
3. ✅ **Add** more recipients in `system_users` table
4. ✅ **Monitor** usage and costs
5. ✅ **Upgrade** to production WhatsApp (optional)

---

## 📞 Support

### Twilio Support
- **Documentation**: [https://www.twilio.com/docs](https://www.twilio.com/docs)
- **Support**: [https://support.twilio.com](https://support.twilio.com)
- **Community**: [https://www.twilio.com/community](https://www.twilio.com/community)

### Khareetaty AI Support
- **Email**: bader.naser.ai.sa@gmail.com
- **Documentation**: See `README.md`, `QUICK_START.md`, `TESTING_GUIDE.md`

---

## 🎉 Success!

Your Khareetaty AI platform is now configured for real-time WhatsApp and SMS alerts!

**What You Can Do Now:**
- Receive hotspot alerts automatically
- Send manual alerts from command dashboard
- Monitor alert delivery in Twilio Console
- Scale to multiple recipients

**Welcome to operational crime intelligence! 🚨🇰🇼**

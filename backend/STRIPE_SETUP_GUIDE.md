# Stripe Setup Guide for Noisemaker

Complete guide to setting up Stripe for your music promotion SaaS.

---

## Part 1: Create Your Stripe Account

### Step 1: Sign Up
1. Go to https://stripe.com
2. Click "Start now" or "Sign up"
3. Enter business email and create password
4. **Business Type**: Select "Company" or "Individual" (recommend Company for SaaS)
5. **Country**: United States (or your operating country)
6. **Business Name**: "Noisemaker" or your registered business name

### Step 2: Verify Your Business
Stripe will ask for:
- Business EIN or SSN
- Bank account for payouts
- Business address
- Personal ID verification (driver's license/passport)

**Note**: You can start in **Test Mode** immediately without completing verification. Do this first while building!

---

## Part 2: Enable Test Mode

### Critical Settings for Development:

1. **Toggle to Test Mode** (top-right corner of dashboard)
   - Shows "Test mode" with orange background
   - All transactions are fake - no real money moves
   - Use test card: `4242 4242 4242 4242`

2. **Get Your Test API Keys**:
   - Go to: Developers → API keys
   - Copy these (save in `.env` file):
     - `STRIPE_TEST_SECRET_KEY=sk_test_...` (starts with `sk_test_`)
     - `STRIPE_TEST_PUBLISHABLE_KEY=pk_test_...` (starts with `pk_test_`)

---

## Part 3: Configure Products for Noisemaker

### Create Subscription Products:

1. **Go to**: Products → Create product

2. **Create 3 Subscription Tiers**:

#### Product 1: Talent
   - **Name**: "Talent"
   - **Description**: "2 platforms, perfect for emerging artists"
   - **Pricing**:
     - Model: Recurring
     - Price: $20.00 USD
     - Billing period: Monthly
   - **Metadata**: `{"tier": "talent", "platforms": "2"}`
   - **Save price ID**: `price_xxxxxxxxxxxxx` (copy this!)

#### Product 2: Star
   - **Name**: "Star"
   - **Description**: "5 platforms with priority support"
   - **Pricing**:
     - Model: Recurring
     - Price: $40.00 USD
     - Billing period: Monthly
   - **Metadata**: `{"tier": "star", "platforms": "5"}`
   - **Save price ID**: `price_xxxxxxxxxxxxx`

#### Product 3: Legend
   - **Name**: "Legend"
   - **Description**: "All 8 platforms with custom branding"
   - **Pricing**:
     - Model: Recurring
     - Price: $60.00 USD
     - Billing period: Monthly
   - **Metadata**: `{"tier": "legend", "platforms": "8"}`
   - **Save price ID**: `price_xxxxxxxxxxxxx`

### Create Extended Song Product:

#### Product 4: Extended Song Promotion
   - **Name**: "Extended Song Promotion"
   - **Description**: "Extend a qualified song beyond 42 days"
   - **Pricing**:
     - Model: Recurring
     - Price: $10.00 USD
     - Billing period: Monthly
   - **Save price ID**: `price_xxxxxxxxxxxxx`

### Create Marketplace Products:

#### Product 5: Single Artwork
   - **Name**: "Album Artwork - Single"
   - **Description**: "Download 1 exclusive album artwork"
   - **Pricing**:
     - Model: One-time
     - Price: $2.99 USD
   - **Save price ID**: `price_xxxxxxxxxxxxx`

#### Product 6: Artwork 5-Pack
   - **Name**: "Album Artwork - 5 Pack"
   - **Description**: "Download 5 exclusive album artworks"
   - **Pricing**:
     - Model: One-time
     - Price: $9.99 USD
   - **Save price ID**: `price_xxxxxxxxxxxxx`

#### Product 7: Artwork 15-Pack
   - **Name**: "Album Artwork - 15 Pack"
   - **Description**: "Download 15 exclusive album artworks"
   - **Pricing**:
     - Model: One-time
     - Price: $19.99 USD
   - **Save price ID**: `price_xxxxxxxxxxxxx`

---

## Part 4: Configure Webhooks

### Why Webhooks?
Webhooks notify your server when events happen (payment success, subscription canceled, etc.)

### Setup Steps:

1. **Go to**: Developers → Webhooks → Add endpoint

2. **Endpoint URL**:
   - Test Mode: `https://your-domain.com/api/payment/webhooks/stripe` (use ngrok for local testing)
   - Production: `https://api.noisemaker.doowopp.com/api/payment/webhooks/stripe`

3. **Select Events to Listen For**:
   ```
   ✅ payment_intent.succeeded
   ✅ payment_intent.payment_failed
   ✅ customer.subscription.created
   ✅ customer.subscription.updated
   ✅ customer.subscription.deleted
   ✅ invoice.payment_succeeded
   ✅ invoice.payment_failed
   ✅ checkout.session.completed
   ```

4. **Copy Webhook Signing Secret**:
   - Save as: `STRIPE_WEBHOOK_SECRET=whsec_...`
   - **Critical**: Used to verify webhook authenticity

---

## Part 5: Environment Variables Setup

Create `.env` file in project root:

```bash
# Stripe API Keys (TEST MODE)
STRIPE_TEST_SECRET_KEY=sk_test_YOUR_KEY_HERE
STRIPE_TEST_PUBLISHABLE_KEY=pk_test_YOUR_KEY_HERE
STRIPE_WEBHOOK_SECRET=whsec_YOUR_SECRET_HERE

# Stripe Price IDs (Test Mode)
STRIPE_PRICE_TALENT=price_xxxxxxxxxxxxx
STRIPE_PRICE_STAR=price_xxxxxxxxxxxxx
STRIPE_PRICE_LEGEND=price_xxxxxxxxxxxxx
STRIPE_PRICE_EXTENDED_SONG=price_xxxxxxxxxxxxx
STRIPE_PRICE_ARTWORK_SINGLE=price_xxxxxxxxxxxxx
STRIPE_PRICE_ARTWORK_5PACK=price_xxxxxxxxxxxxx
STRIPE_PRICE_ARTWORK_15PACK=price_xxxxxxxxxxxxx

# When ready for production, add:
# STRIPE_LIVE_SECRET_KEY=sk_live_YOUR_KEY_HERE
# STRIPE_LIVE_PUBLISHABLE_KEY=pk_live_YOUR_KEY_HERE
```

---

## Part 6: Critical Settings in Stripe Dashboard

### 1. Enable Customer Portal
- **Go to**: Settings → Billing → Customer portal
- **Enable**: "Allow customers to manage subscriptions"
- **Settings**:
  - ✅ Cancel subscriptions
  - ✅ Update payment methods
  - ✅ View invoices
  - ✅ Update billing information

### 2. Configure Email Notifications
- **Go to**: Settings → Emails
- **Enable**:
  - ✅ Successful payments
  - ✅ Failed payments
  - ✅ Subscription created
  - ✅ Subscription canceled
  - ✅ Upcoming invoice (7 days before)

### 3. Set Up Tax Handling (Optional but Recommended)
- **Go to**: Settings → Tax → Stripe Tax
- **Enable**: Automatic tax calculation
- **Note**: Stripe charges 0.5% + $0.02 per transaction for this

### 4. Configure Retry Logic for Failed Payments
- **Go to**: Settings → Billing → Subscriptions and emails
- **Smart Retries**: Enable (Stripe auto-retries failed payments)
- **Retry schedule**:
  - Day 3, Day 5, Day 7, Day 10
  - After 4 retries, subscription canceled

---

## Part 7: Test Card Numbers

Use these in Test Mode:

### Successful Payments:
```
4242 4242 4242 4242  (Visa)
5555 5555 5555 4444  (Mastercard)
```

### Test Failed Payments:
```
4000 0000 0000 0002  (Card declined)
4000 0000 0000 9995  (Insufficient funds)
```

### Test 3D Secure (SCA):
```
4000 0025 0000 3155  (Requires authentication)
```

**For all test cards**:
- Expiry: Any future date (e.g., 12/25)
- CVC: Any 3 digits (e.g., 123)
- ZIP: Any 5 digits (e.g., 12345)

---

## Part 8: Security Checklist

Before going live:

- [ ] **Never expose secret keys** - keep in `.env`, never in git
- [ ] **Verify webhook signatures** - prevent fake webhook attacks
- [ ] **Use HTTPS only** - required for production
- [ ] **Implement idempotency keys** - prevent duplicate charges
- [ ] **Enable Stripe Radar** - automatic fraud detection (included free)
- [ ] **Set up 2FA** on Stripe account - protect from account takeover
- [ ] **Review PCI compliance** - Stripe handles card data, but follow best practices

---

## Part 9: Going Live Checklist

When ready to accept real payments:

1. **Complete business verification** in Stripe dashboard
2. **Add bank account** for payouts
3. **Request to activate live mode** (if not auto-activated)
4. **Get live API keys** from Developers → API keys
5. **Update `.env`** with live keys (keep test keys for development)
6. **Recreate products in live mode** (products don't transfer from test → live)
7. **Update webhook endpoint** to production URL
8. **Test with real credit card** (start with $1 test charge to yourself)
9. **Monitor first week closely** - check dashboard daily for issues

---

## Part 10: Monitoring & Maintenance

### Daily/Weekly:
- Check Dashboard → Home for failed payments
- Review Dashboard → Payments for trends
- Monitor Dashboard → Disputes (chargebacks)

### Monthly:
- Review Dashboard → Reports → Revenue
- Check Dashboard → Customers → Churn rate
- Analyze Dashboard → Analytics → Conversion funnel

### Set Up Alerts:
- Go to: Developers → Webhooks → Configure alerts
- Email alerts for: Failed payments, Disputes, High-value transactions

---

## Part 11: Common Issues & Solutions

### Issue: "No such customer"
**Solution**: Create Stripe customer when user signs up:
```python
customer = stripe.Customer.create(email=user_email, metadata={'user_id': user_id})
```

### Issue: "Webhook signature verification failed"
**Solution**: Check `STRIPE_WEBHOOK_SECRET` is correct and using raw request body

### Issue: "Payment requires authentication" (3D Secure)
**Solution**: Implement Stripe.js payment flow with `handleCardAction()`

### Issue: "Card declined"
**Solution**: Ask user to try different card or contact their bank

---

## Part 12: Useful Resources

- **Stripe Dashboard**: https://dashboard.stripe.com
- **API Docs**: https://stripe.com/docs/api
- **Webhooks Guide**: https://stripe.com/docs/webhooks
- **Testing Guide**: https://stripe.com/docs/testing
- **Python Library**: https://stripe.com/docs/api/python
- **Support**: support@stripe.com (24/7 email support)

---

## Next Steps

After completing Stripe setup:

1. ✅ Save all API keys and Price IDs in `.env`
2. ✅ Test in Test Mode first
3. ✅ Implement Stripe integration in code (Phase 3)
4. ✅ Test all payment flows thoroughly
5. ✅ Complete business verification
6. ✅ Go live!

---

**Questions?** Review Stripe's extensive documentation or contact their support team. They're very helpful!

**Remember**: Start in TEST MODE and don't switch to live until your integration is fully tested and working perfectly.

# Hugging Face Deployment Guide

## Prerequisites

- [ ] Hugging Face account created at https://huggingface.co/join
- [ ] Logged into Hugging Face
- [ ] Ready to create 5 new Spaces

---

## Deployment Steps

### Step 1: Create Hugging Face Spaces

You need to create 5 separate Spaces, one for each repository.

#### Space 1: insurance-datasets-synthetic

1. Go to https://huggingface.co/new-space
2. **Owner**: Select your username
3. **Space name**: `insurance-datasets-synthetic`
4. **License**: MIT
5. **Select SDK**: Gradio
6. **Gradio SDK version**: 4.44.0
7. **Space hardware**: CPU basic (free)
8. **Visibility**: Public
9. Click **Create Space**

#### Space 2: fraud-triage-sandbox

1. Go to https://huggingface.co/new-space
2. **Owner**: Select your username
3. **Space name**: `fraud-triage-sandbox`
4. **License**: MIT
5. **Select SDK**: Gradio
6. **Gradio SDK version**: 4.44.0
7. **Space hardware**: CPU basic (free)
8. **Visibility**: Public
9. Click **Create Space**

#### Space 3: ifrs-claim-accrual-estimator

1. Go to https://huggingface.co/new-space
2. **Owner**: Select your username
3. **Space name**: `ifrs-claim-accrual-estimator`
4. **License**: MIT
5. **Select SDK**: Gradio
6. **Gradio SDK version**: 4.44.0
7. **Space hardware**: CPU basic (free)
8. **Visibility**: Public
9. Click **Create Space**

#### Space 4: doc-rag-compliance-assistant

1. Go to https://huggingface.co/new-space
2. **Owner**: Select your username
3. **Space name**: `doc-rag-compliance-assistant`
4. **License**: MIT
5. **Select SDK**: Gradio
6. **Gradio SDK version**: 4.44.0
7. **Space hardware**: CPU basic (free)
8. **Visibility**: Public
9. Click **Create Space**

#### Space 5: gcc-insurance-ai-hub

1. Go to https://huggingface.co/new-space
2. **Owner**: Select your username
3. **Space name**: `gcc-insurance-ai-hub`
4. **License**: MIT
5. **Select SDK**: Gradio
6. **Gradio SDK version**: 4.44.0
7. **Space hardware**: CPU basic (free)
8. **Visibility**: Public
9. Click **Create Space**

---

### Step 2: Upload Files to Each Space

#### Method A: Web Interface (Recommended for beginners)

For each Space:

1. After creating the Space, you'll see "Files" tab
2. Click "Add file" > "Upload files"
3. Navigate to the repository folder on your computer
4. Select ALL files from that repository
5. Click "Commit changes to main"

**Files to upload per repository:**

**Space 1 (insurance-datasets-synthetic):**
- app.py
- requirements.txt
- README.md
- model_card.md
- data_loader.py
- claims.csv
- policies.csv
- fraud_indicators.csv

**Space 2 (fraud-triage-sandbox):**
- app.py
- requirements.txt
- README.md
- model_card.md
- fraud_detector.py

**Space 3 (ifrs-claim-accrual-estimator):**
- app.py
- requirements.txt
- README.md
- model_card.md
- estimator.py

**Space 4 (doc-rag-compliance-assistant):**
- app.py
- requirements.txt
- README.md
- model_card.md
- rag_engine.py

**Space 5 (gcc-insurance-ai-hub):**
- app.py
- requirements.txt
- README.md
- model_card.md

#### Method B: Git (Advanced users)

For each Space:

```bash
# Clone the Space repository
git clone https://huggingface.co/spaces/YOUR_USERNAME/SPACE_NAME
cd SPACE_NAME

# Copy files from local repository
cp /Users/bdr.ai/huggingface-insurance-repos/REPO_NAME/* .

# Add, commit, and push
git add .
git commit -m "Initial commit"
git push
```

---

### Step 3: Wait for Build

After uploading files:

1. Hugging Face will automatically build your Space
2. Watch the "Building" status in the Space
3. Wait for status to change to "Running"
4. This usually takes 1-3 minutes

---

### Step 4: Test Each Space

#### Test Space 1: insurance-datasets-synthetic
- [ ] Space loads without errors
- [ ] Can see dataset tabs
- [ ] Can view claims data
- [ ] Can view policies data
- [ ] Can view fraud indicators
- [ ] Can filter data
- [ ] Can download CSVs

#### Test Space 2: fraud-triage-sandbox
- [ ] Space loads without errors
- [ ] Can enter claim details
- [ ] Can adjust thresholds
- [ ] Click "Analyze Claim" works
- [ ] Risk score displays
- [ ] Triage decision shows
- [ ] Explanation appears

#### Test Space 3: ifrs-claim-accrual-estimator
- [ ] Space loads without errors
- [ ] Can enter claim information
- [ ] Can select claim type
- [ ] Can adjust parameters
- [ ] Click "Calculate Accrual" works
- [ ] Summary displays
- [ ] Breakdown table shows

#### Test Space 4: doc-rag-compliance-assistant
- [ ] Space loads without errors
- [ ] Can enter questions
- [ ] Can adjust number of documents
- [ ] Click "Ask Question" works
- [ ] Answer displays
- [ ] Source documents show
- [ ] Example buttons work

#### Test Space 5: gcc-insurance-ai-hub
- [ ] Space loads without errors
- [ ] All accordions expand
- [ ] All descriptions visible
- [ ] Links are present (will update in next step)

---

### Step 5: Update Hub URLs

Once all Spaces are deployed and working:

1. Note your Hugging Face username
2. Open `gcc-insurance-ai-hub/app.py`
3. Replace all instances of `YOUR_USERNAME` with your actual username
4. Re-upload the updated `app.py` to the hub Space
5. Wait for rebuild
6. Test that all links work

**Example:**
If your username is `john-doe`, change:
```
https://huggingface.co/spaces/YOUR_USERNAME/insurance-datasets-synthetic
```
to:
```
https://huggingface.co/spaces/john-doe/insurance-datasets-synthetic
```

---

### Step 6: Final Verification

- [ ] All 5 Spaces are running
- [ ] All Spaces tested and working
- [ ] Hub links updated
- [ ] Hub links tested and working
- [ ] No errors in any Space
- [ ] All features functional

---

## Troubleshooting

### Space won't build

**Check:**
- All required files uploaded?
- requirements.txt present?
- app.py present?
- No syntax errors in code?

**Solution:**
- Review build logs in Space
- Fix any errors
- Re-upload corrected files

### Space builds but shows error

**Check:**
- Build logs for error messages
- All dependencies in requirements.txt
- Python version compatibility

**Solution:**
- Check Gradio version matches (4.44.0)
- Verify all imports are available
- Check for typos in code

### Links in hub don't work

**Check:**
- Did you update YOUR_USERNAME?
- Are Space names exactly correct?
- Are Spaces set to Public?

**Solution:**
- Double-check username spelling
- Verify Space names match exactly
- Ensure Spaces are public, not private

---

## Post-Deployment

### Share Your Spaces

Once deployed, you can share:
- Direct Space URLs
- Hub URL (central access point)
- Embed Spaces in websites
- Share on social media

### Monitor Usage

- Check Space analytics in HF dashboard
- Review any community feedback
- Monitor for errors or issues

### Maintenance

- Update code as needed
- Fix bugs if reported
- Add features based on feedback
- Keep dependencies updated

---

## Quick Reference

### Space URLs (after deployment)

Replace `YOUR_USERNAME` with your actual username:

1. https://huggingface.co/spaces/YOUR_USERNAME/insurance-datasets-synthetic
2. https://huggingface.co/spaces/YOUR_USERNAME/fraud-triage-sandbox
3. https://huggingface.co/spaces/YOUR_USERNAME/ifrs-claim-accrual-estimator
4. https://huggingface.co/spaces/YOUR_USERNAME/doc-rag-compliance-assistant
5. https://huggingface.co/spaces/YOUR_USERNAME/gcc-insurance-ai-hub

### Local File Paths

1. /Users/bdr.ai/huggingface-insurance-repos/insurance-datasets-synthetic/
2. /Users/bdr.ai/huggingface-insurance-repos/fraud-triage-sandbox/
3. /Users/bdr.ai/huggingface-insurance-repos/ifrs-claim-accrual-estimator/
4. /Users/bdr.ai/huggingface-insurance-repos/doc-rag-compliance-assistant/
5. /Users/bdr.ai/huggingface-insurance-repos/gcc-insurance-ai-hub/

---

## Support

If you encounter issues:

1. Check Hugging Face documentation: https://huggingface.co/docs/hub/spaces
2. Review Space build logs
3. Check Gradio documentation: https://gradio.app/docs
4. Ask in Hugging Face forums: https://discuss.huggingface.co/

---

**Good luck with your deployment!**

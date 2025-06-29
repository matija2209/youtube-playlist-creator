# 🚀 OAuth2 Setup Guide - YouTube Playlist Creator

## 📋 **Overview**
This guide will help you set up **dual OAuth2 authentication** for the YouTube Playlist Creator:
- **Desktop OAuth**: For immediate CLI testing
- **Web OAuth**: For future multi-user production via FastAPI

## 🎯 **What You'll Accomplish**
- ✅ Create real OAuth2 credentials in Google Cloud Console
- ✅ Enable YouTube Data API v3
- ✅ Test desktop OAuth flow for CLI usage
- ✅ Test web OAuth flow for API endpoints
- ✅ Verify full integration with playlist creation

---

## 📚 **Phase 1: Google Cloud Console Setup**

### **Step 1.1: Create/Access Google Cloud Project**

1. **Go to Google Cloud Console**
   ```
   https://console.cloud.google.com/
   ```

2. **Create or select project**
   - If project doesn't exist, create: `youtube-playlist-creator-oauth`
   - Or use existing project name

3. **Note your project ID** - you'll need it later

### **Step 1.2: Enable YouTube Data API v3**

1. **Go to APIs & Services → Library**
   ```
   https://console.cloud.google.com/apis/library
   ```

2. **Search for "YouTube Data API v3"**
   - Click on "YouTube Data API v3"
   - Click **"ENABLE"**
   - ✅ Wait for confirmation

### **Step 1.3: Create Desktop OAuth2 Client**

1. **Go to Credentials page**
   ```
   https://console.cloud.google.com/apis/credentials
   ```

2. **Click "CREATE CREDENTIALS" → "OAuth 2.0 Client IDs"**

3. **Configure OAuth consent screen** (if not done yet)
   - Choose "External" (or "Internal" if G Suite)
   - Fill required fields:
     - App name: `YouTube Playlist Creator`
     - User support email: Your email
     - App domain: Leave blank for testing
     - Contact email: Your email
   - **Save**

4. **Create Desktop Application**
   - Application type: **"Desktop application"**
   - Name: `YouTube Playlist Creator - Desktop`
   - Click **"CREATE"**

5. **Download credentials**
   - Click **"DOWNLOAD JSON"**
   - Save as `client_secrets.json` in project root
   - ⚠️ **IMPORTANT**: Must be named exactly `client_secrets.json`

### **Step 1.4: Create Web OAuth2 Client**

1. **Create another OAuth 2.0 Client ID**
   - Application type: **"Web application"**
   - Name: `YouTube Playlist Creator - Web`

2. **Add Authorized redirect URIs**:
   ```
   http://localhost:3000/oauth/callback
   http://127.0.0.1:3000/oauth/callback
   ```

3. **Download credentials**
   - Save as `web_client_secrets.json` in project root
   - ⚠️ **IMPORTANT**: Must be named exactly `web_client_secrets.json`

### **Step 1.5: Verify File Structure**

Your project root should now have:
```
youtube-playlist-creator/
├── client_secrets.json          # ← Desktop OAuth (REAL credentials)
├── web_client_secrets.json      # ← Web OAuth (REAL credentials)
├── test_desktop_oauth.py        # ← Test scripts
├── test_web_oauth.py            # ← Test scripts  
├── test_full_integration.py     # ← Test scripts
└── ...
```

---

## 🧪 **Phase 2: Test Desktop OAuth**

### **Step 2.1: Run Desktop OAuth Test**

```bash
# Make sure you're in the project root
cd youtube-playlist-creator

# Run desktop OAuth test
python test_desktop_oauth.py
```

**Expected behavior:**
1. ✅ Script verifies `client_secrets.json` has real credentials
2. 🌐 Opens browser automatically
3. 📋 You log in to Google and grant permissions
4. ✅ Returns to script with success message
5. 💾 Creates `token.json` file
6. 👤 Shows your channel information

### **Step 2.2: Troubleshooting Desktop OAuth**

**If you see "client_secrets.json contains placeholder values":**
- ❌ You haven't replaced the placeholder file
- ✅ Re-download from Google Cloud Console

**If you see "Invalid client" error:**
- ❌ Credentials are wrong or project mismatch
- ✅ Verify you downloaded from correct project

**If browser doesn't open:**
- ⚠️ Script will show manual instructions
- ✅ Copy URL and complete manual flow

**If "Access denied" during login:**
- ❌ YouTube Data API v3 not enabled
- ✅ Return to Step 1.2

---

## 🌐 **Phase 3: Test Web OAuth**

### **Step 3.1: Run Web OAuth Test**

```bash
python test_web_oauth.py
```

**Expected behavior:**
1. ✅ Script verifies `web_client_secrets.json` has real credentials
2. 🔗 Generates authorization URL
3. 📋 You manually copy URL and complete OAuth flow
4. ✅ Shows token exchange success

### **Step 3.2: Complete Web OAuth Flow**

1. **Copy the authorization URL** from script output
2. **Open in browser** and log in to Google
3. **Grant permissions**
4. **After redirect**, you'll see URL like:
   ```
   http://localhost:3000/oauth/callback?code=4/0AX4XfWh...&scope=https://www.googleapis.com/auth/youtube...
   ```
5. **Copy the `code` parameter** (everything after `code=` and before `&`)
6. **Paste it back into the script**

### **Step 3.3: Test FastAPI Integration**

After web OAuth test succeeds:

```bash
# Start FastAPI server in one terminal
uvicorn app.main:app --reload --port 3000

# In another terminal, run web OAuth test with integration
python test_web_oauth.py
# Choose 'y' when asked to test FastAPI integration
```

---

## 🎵 **Phase 4: Test Full Integration**

### **Step 4.1: Run Full Integration Test**

```bash
python test_full_integration.py
```

**This will test:**
1. ✅ CSV parsing with `csv_files/sample.csv`
2. ✅ YouTube search functionality
3. ✅ Demo playlist creation (no actual YouTube playlist)
4. ✅ Real playlist creation with OAuth (if you choose)

### **Step 4.2: Understanding the Test Results**

**Demo Mode Results:**
- Shows how many songs were found on YouTube
- Lists songs that couldn't be found
- Gives success rate percentage

**Real Playlist Creation:**
- Creates actual private YouTube playlist
- Provides playlist URL
- Shows final song count

---

## 🔧 **Phase 5: Verify CLI Works**

### **Step 5.1: Test CLI with OAuth**

```bash
# Test CLI help
python -m app.cli --help

# Test demo mode
python -m app.cli create-demo-playlist csv_files/sample.csv "My Test Playlist"

# Test real playlist creation
python -m app.cli create-playlist csv_files/sample.csv "My Real Playlist" --privacy private
```

### **Step 5.2: Test FastAPI Endpoints**

```bash
# Start server
uvicorn app.main:app --reload --port 3000

# Test in browser:
# http://localhost:3000/
# http://localhost:3000/oauth/status
# http://localhost:3000/oauth/login
# http://localhost:3000/docs
```

---

## 🎉 **Success Criteria**

**✅ Desktop OAuth Working When:**
- `python test_desktop_oauth.py` succeeds
- Shows your YouTube channel info
- Creates `token.json` file
- CLI commands work with real playlists

**✅ Web OAuth Working When:**
- `python test_web_oauth.py` succeeds
- Can generate authorization URLs
- Can exchange codes for tokens
- FastAPI endpoints return proper responses

**✅ Full Integration Working When:**
- `python test_full_integration.py` succeeds
- Demo mode finds songs successfully
- Real playlist creation works
- All service health checks pass

---

## 🚨 **Common Issues & Solutions**

### **Issue: "OAuth client secrets file not found"**
**Solution:**
- Ensure files are named exactly `client_secrets.json` and `web_client_secrets.json`
- Check they're in the project root directory

### **Issue: "Invalid client credentials"**
**Solution:**
- Verify you downloaded from the correct Google Cloud project
- Check project ID matches your setup
- Re-download credentials from Google Cloud Console

### **Issue: "Redirect URI mismatch"**
**Solution:**
- Ensure redirect URIs in Google Cloud Console match exactly:
  - Desktop: `http://localhost:3000` (and `urn:ietf:wg:oauth:2.0:oob`)
  - Web: `http://localhost:3000/oauth/callback`

### **Issue: "Access denied" during OAuth****
**Solution:**
- Verify YouTube Data API v3 is enabled
- Check OAuth consent screen is configured
- Try different Google account if restricted

### **Issue: "Token expired" errors**
**Solution:**
- Delete `token.json` and `web_token.json` files
- Re-run tests with fresh authentication

---

## 🔒 **Security Notes**

1. **Never commit credential files to git**
   - `client_secrets.json` and `web_client_secrets.json` are in `.gitignore`

2. **Keep tokens secure**
   - `token.json` and `web_token.json` contain access tokens
   - Also in `.gitignore`

3. **Use private playlists for testing**
   - Avoids cluttering your public channel

---

## 🚀 **Next Steps After Setup**

1. **For Development:**
   - Use desktop OAuth for quick CLI testing
   - Test with small CSV files first

2. **For Production:**
   - Web OAuth is ready for multi-user scenarios
   - Add proper user session management
   - Implement per-user token storage

3. **For Deployment:**
   - Set up proper environment variables
   - Configure production redirect URIs
   - Add error monitoring

---

## 📞 **Getting Help**

If you encounter issues:

1. **Check the logs** - scripts show detailed error information
2. **Run tests individually** - isolate the problem
3. **Verify Google Cloud Console** - ensure APIs are enabled
4. **Check file permissions** - ensure credentials are readable

**Most issues are related to:**
- ❌ Placeholder credentials not replaced
- ❌ Wrong file names
- ❌ YouTube Data API v3 not enabled
- ❌ Redirect URI mismatches

Good luck! 🎵 
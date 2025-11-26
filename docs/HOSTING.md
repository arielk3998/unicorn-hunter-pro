# Hosting Your Own Download Server

This guide explains how to host Unicorn Hunter downloads on your own website or server as an alternative to GitHub releases.

## Overview

You have two main options:
1. **GitHub Releases** (easiest, free) - Users download from GitHub
2. **Custom Website** (more control) - Host downloads on your own domain

## Option 1: GitHub Releases (Current Setup)

**Pros:**
- ✅ Free unlimited bandwidth
- ✅ Automatic builds via GitHub Actions
- ✅ Version tracking built-in
- ✅ No server maintenance

**Cons:**
- ❌ Requires users to have GitHub access (public repos are fine)
- ❌ Less branding control

Already configured! Just push a git tag to trigger a release.

## Option 2: Custom Website Hosting

### Static File Hosting

Host pre-built executables on any web server or CDN.

#### A. Simple Static Hosting (e.g., Netlify, Vercel, GitHub Pages)

1. **Build executables locally**:
   ```powershell
   ./scripts/build_release.ps1
   ```

2. **Create download page** (`public/downloads.html`):
   ```html
   <!DOCTYPE html>
   <html>
   <head>
       <title>Download Unicorn Hunter Pro</title>
       <meta name="viewport" content="width=device-width, initial-scale=1">
       <style>
           body { font-family: Arial, sans-serif; max-width: 800px; margin: 50px auto; padding: 20px; }
           .download-btn { display: inline-block; padding: 15px 30px; margin: 10px;
                          background: #4CAF50; color: white; text-decoration: none; border-radius: 5px; }
           .download-btn:hover { background: #45a049; }
       </style>
   </head>
   <body>
       <h1>🦄 Download Unicorn Hunter Pro</h1>
       <p>Free AI-powered job application tracker</p>
       
       <h2>Choose Your Platform</h2>
       <a href="releases/UnicornHunter-Windows.zip" class="download-btn">🪟 Windows</a>
       <a href="releases/UnicornHunter-macOS.tar.gz" class="download-btn">🍎 macOS</a>
       <a href="releases/UnicornHunter-Linux.tar.gz" class="download-btn">🐧 Linux</a>
       
       <h2>Installation</h2>
       <ol>
           <li>Download the file for your operating system</li>
           <li>Extract the archive</li>
           <li>Run the UnicornHunter executable</li>
       </ol>
       
       <p><small>Version 1.0.0 | <a href="https://github.com/arielk3998/unicorn-hunter-pro">Source Code</a></small></p>
   </body>
   </html>
   ```

3. **Upload files**:
   ```
   public/
   ├── downloads.html
   └── releases/
       ├── UnicornHunter-Windows.zip
       ├── UnicornHunter-macOS.tar.gz
       └── UnicornHunter-Linux.tar.gz
   ```

4. **Deploy** to Netlify/Vercel/GitHub Pages

#### B. CDN Hosting (e.g., AWS S3 + CloudFront, DigitalOcean Spaces)

**AWS S3 Example:**

1. **Create S3 bucket**: `unicorn-hunter-downloads`

2. **Upload files**:
   ```powershell
   aws s3 cp release/ s3://unicorn-hunter-downloads/v1.0.0/ --recursive
   ```

3. **Set public access** (or use CloudFront for better control)

4. **Update download links**:
   ```
   https://unicorn-hunter-downloads.s3.amazonaws.com/v1.0.0/UnicornHunter-Windows.zip
   ```

#### C. Traditional Web Hosting (cPanel, shared hosting)

1. Upload files via FTP to `public_html/downloads/`
2. Create `index.html` with download links
3. Access at `https://yoursite.com/downloads/`

### Automated Deployment

**GitHub Actions to Your Server:**

Add to `.github/workflows/deploy-custom.yml`:

```yaml
name: Deploy to Custom Server

on:
  push:
    tags:
      - 'v*'

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Build executables
        # ... (use existing build steps)
      
      - name: Deploy to server via SCP
        uses: appleboy/scp-action@master
        with:
          host: ${{ secrets.SERVER_HOST }}
          username: ${{ secrets.SERVER_USER }}
          key: ${{ secrets.SERVER_SSH_KEY }}
          source: "release/*"
          target: "/var/www/html/downloads/"
```

Store credentials in GitHub Secrets.

## Option 3: Hybrid Approach

**Best of both worlds:**

1. Keep GitHub Releases for developers/technical users
2. Add custom branded download page linking to GitHub release assets:

```html
<a href="https://github.com/arielk3998/unicorn-hunter-pro/releases/latest/download/UnicornHunter-Windows.zip">
    Download for Windows
</a>
```

This way you control the landing page but leverage GitHub's infrastructure.

## Custom Domain Setup

### For GitHub Releases
Point your domain's download subdomain to GitHub:

1. Add CNAME record: `download.yoursite.com` → `arielk3998.github.io`
2. Configure GitHub Pages in repository settings
3. Update links to use custom domain

### For Custom Hosting
Standard DNS setup:
- **A record**: Point to your server IP
- **CNAME**: Point subdomain to CDN

## Download Analytics

Track downloads by:

1. **Server logs** (if self-hosting)
2. **Google Analytics** on download page
3. **GitHub Insights** (for GitHub releases)
4. **CDN analytics** (CloudFront, Cloudflare)

## Security Considerations

1. **Sign executables** (Windows code signing, macOS notarization)
2. **Provide checksums**:
   ```powershell
   Get-FileHash dist/UnicornHunter.exe -Algorithm SHA256 | Select-Object Hash
   ```
3. **HTTPS only** - Use SSL certificates
4. **Virus scan** uploads before hosting

## Cost Comparison

| Platform | Cost | Bandwidth | Ease |
|----------|------|-----------|------|
| GitHub Releases | Free | Unlimited | ⭐⭐⭐⭐⭐ |
| Netlify | Free tier OK | 100GB/mo free | ⭐⭐⭐⭐ |
| AWS S3 + CloudFront | ~$1-5/mo | Pay per GB | ⭐⭐⭐ |
| Shared Hosting | $5-20/mo | Usually unlimited | ⭐⭐⭐⭐ |

## Recommendation

**For now**: Use GitHub Releases (already configured!)

**When you're ready for custom hosting**:
1. Create a simple landing page on your domain
2. Link to GitHub release assets (hybrid approach)
3. Optionally add Google Analytics
4. Later migrate to full custom hosting if needed

## Next Steps

To enable downloads now:

```powershell
# Create your first release
./scripts/prepare_release.ps1 -Version 1.0.0
```

This will:
- Build executables for all platforms
- Create GitHub release
- Make downloads available at GitHub URLs
- You can then add custom landing page pointing to these URLs

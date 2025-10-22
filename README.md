# Automated Waydroid Image OBS Packager

[![Build Status](https://img.shields.io/github/actions/workflow/status/itachi-re/waydroid-image-obs-packager/update-images.yml?style=flat-square)](https://github.com/itachi-re/waydroid-image-obs/actions)
[![Open Build Service](https://img.shields.io/badge/OBS-Package-blue?style=flat-square&logo=openbuildservice)](https://build.opensuse.org/package/show/home:itachi_re/waydroid-image)

This project automatically builds and packages the latest [Waydroid](https://waydro.id/) system and vendor images as RPM packages for compatible Linux distributions. It's designed to work with the Open Build Service (OBS) and uses GitHub Actions to keep the image URLs current.

## ✨ Features

- **Automated Updates**: Daily checks for new Waydroid image releases
- **Multi-Flavor Support**: Builds packages for multiple Android variants and GApps configurations
- **OBS Integration**: Seamless integration with Open Build Service for automated package building
- **Version Tracking**: Automatic version numbering based on image release dates
- **Cache System**: Prevents unnecessary updates when no new images are available

## 🚀 How It Works

### Automated Pipeline

```mermaid
graph LR
    A[GitHub Actions] --> B[Scrape SourceForge]
    B --> C[Update Spec File]
    C --> D[Commit Changes]
    D --> E[OBS Trigger]
    E --> F[Build RPMs]
    F --> G[Package Repository]
```

1. **Daily Automation**: A GitHub Actions workflow (`.github/workflows/update-images.yml`) runs daily
2. **Web Scraping**: The `update_waydroid_latest.py` script scrapes the Waydroid SourceForge project page to find the latest system and vendor image download URLs
3. **Spec File Update**: The script updates `waydroid-image.spec` with new URLs and sets the package version to match the latest image date
4. **Automatic Commit**: If new images are found, the GitHub Action commits the updated `waydroid-image.spec` and `waydroid-urls.json` files
5. **OBS Building**: Open Build Service monitors the repository and automatically rebuilds packages when changes are detected

### OBS Integration

The `_service` file configures OBS to:
- Fetch the latest code from the `main` branch
- Use `_multibuild` to build packages for all defined flavors
- Download image ZIP files from the `Source` URLs in the spec file

## 📦 Supported Flavors

| Flavor | Android Version | GApps | Description |
|--------|----------------|-------|-------------|
| `lineage-20-vanilla` | LineageOS 20 (Android 13) | ❌ | Clean AOSP experience |
| `lineage-20-gapps` | LineageOS 20 (Android 13) | ✅ | With Google Apps included |
| `lineage-18-vanilla` | LineageOS 18.1 (Android 11) | ❌ | Legacy AOSP experience |
| `lineage-18-gapps` | LineageOS 18.1 (Android 11) | ✅ | Legacy with Google Apps |

## 🗂️ Project Structure

```
.
├── .github/
│   └── workflows/
│       └── update-images.yml          # Daily update automation
├── waydroid-image.spec                # RPM spec file template
├── _multibuild                        # OBS multi-flavor configuration
├── _service                           # OBS service definitions
├── update_waydroid_latest.py          # URL scraping and update script
└── waydroid-urls.json                 # Cache of latest URLs and versions
```

## 🔧 Usage

### For End Users

Install the Waydroid image packages from your OBS repository:

```bash
# Add the OBS repository (example - replace with actual repo)
zypper addrepo https://download.opensuse.org/repositories/home:your-username/Your_Distribution/ your-waydroid

# Install desired flavor
zypper install waydroid-image-lineage-20-gapps
```

### For Developers/Maintainers

**Manual Update Trigger:**
```bash
python3 update_waydroid_latest.py
```

**Testing Locally:**
```bash
# Build RPM locally (requires rpmbuild)
rpmbuild -ba waydroid-image.spec
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit pull requests for:

- Adding new Waydroid image flavors
- Improving the update script
- Enhancing OBS configuration
- Documentation improvements

## 📄 License

This project is licensed under the [MIT License](LICENSE) - see the LICENSE file for details.

## 🔗 Related Links

- [Waydroid Official Website](https://waydro.id/)
- [Waydroid GitHub](https://github.com/waydroid/waydroid)
- [Open Build Service](https://openbuildservice.org/)
- [LineageOS](https://lineageos.org/)

## ⚠️ Disclaimer

This project is not officially affiliated with Waydroid or LineageOS. It is an automated packaging solution maintained by the community.

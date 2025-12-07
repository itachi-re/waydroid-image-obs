# This file is auto-generated and updated by a GitHub Action.
# Do not edit manually.
# Auto-generated on: 2025-12-07T03:38:22.068832

%global _waydroid_image_dir %{_datadir}/waydroid-extra/images

# Define package details based on flavor
%if "%{?_flavor}" == "lineage-20-gapps"
%define os_version 20
%define os_type gapps
%define flavor_descr LineageOS 20 with Google Apps (GAPPS)
%elseif "%{?_flavor}" == "lineage-20-vanilla"
%define os_version 20
%define os_type vanilla
%define flavor_descr LineageOS 20 Vanilla (AOSP)
%elseif "%{?_flavor}" == "lineage-18-gapps"
%define os_version 18
%define os_type gapps
%define flavor_descr LineageOS 18.1 with Google Apps (GAPPS)
%else
%define _flavor lineage-18-vanilla
%define os_version 18
%define os_type vanilla
%define flavor_descr LineageOS 18.1 Vanilla (AOSP)
%endif

Name:           waydroid-image-%{_flavor}
Version:        20251011
Release:        0
Summary:        %{flavor_descr} images for Waydroid
License:        Apache-2.0
URL:            https://waydro.id/
BuildArch:      noarch
BuildRequires:  unzip

# Source URLs - these are replaced by the update script
# We add #/filename.zip to give each download a unique name
Source0:        https://sourceforge.net/projects/waydroid/files/images/system/lineage/waydroid_x86_64/lineage-20.0-20250823-VANILLA-waydroid_x86_64-system.zip/download#/system-20-vanilla-x86_64.zip
Source1:        https://sourceforge.net/projects/waydroid/files/images/system/lineage/waydroid_x86_64/lineage-20.0-20250809-GAPPS-waydroid_x86_64-system.zip/download#/system-20-gapps-x86_64.zip
Source2:        https://sourceforge.net/projects/waydroid/files/images/vendor/waydroid_x86_64/lineage-20.0-20250809-MAINLINE-waydroid_x86_64-vendor.zip/download#/vendor-20-x86_64.zip
Source3:        https://sourceforge.net/projects/waydroid/files/images/system/lineage/waydroid_arm64/lineage-20.0-20251011-VANILLA-waydroid_arm64-system.zip/download#/system-20-vanilla-arm64.zip
Source4:        https://sourceforge.net/projects/waydroid/files/images/system/lineage/waydroid_arm64/lineage-20.0-20250809-GAPPS-waydroid_arm64-system.zip/download#/system-20-gapps-arm64.zip
Source5:        https://sourceforge.net/projects/waydroid/files/images/vendor/waydroid_arm64/lineage-20.0-20250809-MAINLINE-waydroid_arm64-vendor.zip/download#/vendor-20-arm64.zip

Source10:       https://sourceforge.net/projects/waydroid/files/images/system/lineage/waydroid_x86_64/lineage-18.1-20250628-VANILLA-waydroid_x86_64-system.zip/download#/system-18-vanilla-x86_64.zip
Source11:       https://sourceforge.net/projects/waydroid/files/images/system/lineage/waydroid_x86_64/lineage-18.1-20250628-GAPPS-waydroid_x86_64-system.zip/download#/system-18-gapps-x86_64.zip
Source12:       https://sourceforge.net/projects/waydroid/files/images/vendor/waydroid_x86_64/lineage-18.1-20250628-MAINLINE-waydroid_x86_64-vendor.zip/download#/vendor-18-x86_64.zip
Source13:       https://sourceforge.net/projects/waydroid/files/images/system/lineage/waydroid_arm64/lineage-18.1-20250628-VANILLA-waydroid_arm64-system.zip/download#/system-18-vanilla-arm64.zip
Source14:       https://sourceforge.net/projects/waydroid/files/images/system/lineage/waydroid_arm64/lineage-18.1-20250628-GAPPS-waydroid_arm64-system.zip/download#/system-18-gapps-arm64.zip
Source15:       https://sourceforge.net/projects/waydroid/files/images/vendor/waydroid_arm64/lineage-18.1-20250628-MAINLINE-waydroid_arm64-vendor.zip/download#/vendor-18-arm64.zip

%description
%{summary}.
This package contains the pre-bundled system and vendor images for
Waydroid to use.

%prep
# We don't need to do anything here, OBS downloads the files for us.

%build
# No build steps needed

%install
mkdir -p %{buildroot}%{_waydroid_image_dir}

# Create a temporary directory to extract into,
# so we can reliably rename the file.
%global _tmpdir %{buildroot}/tmp-waydroid
mkdir -p %{_tmpdir}

# Install the correct files based on the flavor
%if "%{?_flavor}" == "lineage-20-gapps"
unzip -oj %{SOURCE1} -d %{_tmpdir}
mv %{_tmpdir}/*.img %{buildroot}%{_waydroid_image_dir}/system.img

unzip -oj %{SOURCE2} -d %{_tmpdir}
mv %{_tmpdir}/*.img %{buildroot}%{_waydroid_image_dir}/vendor.img

%elseif "%{?_flavor}" == "lineage-20-vanilla"
unzip -oj %{SOURCE0} -d %{_tmpdir}
mv %{_tmpdir}/*.img %{buildroot}%{_waydroid_image_dir}/system.img

unzip -oj %{SOURCE2} -d %{_tmpdir}
mv %{_tmpdir}/*.img %{buildroot}%{_waydroid_image_dir}/vendor.img

%elseif "%{?_flavor}" == "lineage-18-gapps"
unzip -oj %{SOURCE11} -d %{_tmpdir}
mv %{_tmpdir}/*.img %{buildroot}%{_waydroid_image_dir}/system.img

unzip -oj %{SOURCE12} -d %{_tmpdir}
mv %{_tmpdir}/*.img %{buildroot}%{_waydroid_image_dir}/vendor.img

%else
# Default to lineage-18-vanilla
unzip -oj %{SOURCE10} -d %{_tmpdir}
mv %{_tmpdir}/*.img %{buildroot}%{_waydroid_image_dir}/system.img

unzip -oj %{SOURCE12} -d %{_tmpdir}
mv %{_tmpdir}/*.img %{buildroot}%{_waydroid_image_dir}/vendor.img
%endif

# Clean up the temporary directory
rm -rf %{_tmpdir}

%files
# Add %dir entries to own the directories
%dir %{_datadir}/waydroid-extra
%dir %{_waydroid_image_dir}
%{_waydroid_image_dir}/system.img
%{_waydroid_image_dir}/vendor.img

%changelog
# Spec file is auto-generated, changelog is not maintained here.

# This file is auto-generated and updated by a GitHub Action.
# Do not edit manually.
# Auto-generated on: 2025-10-25T03:04:40.312831

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

# Source URLs - these are replaced by the update script
Source0:        https://sourceforge.net/projects/waydroid/files/images/system/lineage/waydroid_x86_64/lineage-20.0-20250823-VANILLA-waydroid_x86_64-system.zip/download
Source1:        https://sourceforge.net/projects/waydroid/files/images/system/lineage/waydroid_x86_64/lineage-20.0-20250809-GAPPS-waydroid_x86_64-system.zip/download
Source2:        https://sourceforge.net/projects/waydroid/files/images/vendor/waydroid_x86_64/lineage-20.0-20250809-MAINLINE-waydroid_x86_64-vendor.zip/download
Source3:        https://sourceforge.net/projects/waydroid/files/images/system/lineage/waydroid_arm64/lineage-20.0-20251011-VANILLA-waydroid_arm64-system.zip/download
Source4:        https://sourceforge.net/projects/waydroid/files/images/system/lineage/waydroid_arm64/lineage-20.0-20250809-GAPPS-waydroid_arm64-system.zip/download
Source5:        https://sourceforge.net/projects/waydroid/files/images/vendor/waydroid_arm64/lineage-20.0-20250809-MAINLINE-waydroid_arm64-vendor.zip/download

Source10:       https://sourceforge.net/projects/waydroid/files/images/system/lineage/waydroid_x86_64/lineage-18.1-20250628-VANILLA-waydroid_x86_64-system.zip/download
Source11:       https://sourceforge.net/projects/waydroid/files/images/system/lineage/waydroid_x86_64/lineage-18.1-20250628-GAPPS-waydroid_x86_64-system.zip/download
Source12:       https://sourceforge.net/projects/waydroid/files/images/vendor/waydroid_x86_64/lineage-18.1-20250628-MAINLINE-waydroid_x86_64-vendor.zip/download
Source13:       https://sourceforge.net/projects/waydroid/files/images/system/lineage/waydroid_arm64/lineage-18.1-20250628-VANILLA-waydroid_arm64-system.zip/download
Source14:       https://sourceforge.net/projects/waydroid/files/images/system/lineage/waydroid_arm64/lineage-18.1-20250628-GAPPS-waydroid_arm64-system.zip/download
Source15:       https://sourceforge.net/projects/waydroid/files/images/vendor/waydroid_arm64/lineage-18.1-20250628-MAINLINE-waydroid_arm64-vendor.zip/download

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

# Install the correct files based on the flavor
%if "%{?_flavor}" == "lineage-20-gapps"
unzip -o %{SOURCE1} system.img -d %{buildroot}%{_waydroid_image_dir}
unzip -o %{SOURCE2} vendor.img -d %{buildroot}%{_waydroid_image_dir}
%elseif "%{?_flavor}" == "lineage-20-vanilla"
unzip -o %{SOURCE0} system.img -d %{buildroot}%{_waydroid_image_dir}
unzip -o %{SOURCE2} vendor.img -d %{buildroot}%{_waydroid_image_dir}
%elseif "%{?_flavor}" == "lineage-18-gapps"
unzip -o %{SOURCE11} system.img -d %{buildroot}%{_waydroid_image_dir}
unzip -o %{SOURCE12} vendor.img -d %{buildroot}%{_waydroid_image_dir}
%else
# Default to lineage-18-vanilla
unzip -o %{SOURCE10} system.img -d %{buildroot}%{_waydroid_image_dir}
unzip -o %{SOURCE12} vendor.img -d %{buildroot}%{_waydroid_image_dir}
%endif

%files
%{_waydroid_image_dir}/system.img
%{_waydroid_image_dir}/vendor.img

%changelog
# Spec file is auto-generated, changelog is not maintained here.

# -*- Mode: rpm-spec -*-
#
# This Specfile is based on kernel-tmb spec done by
# Thomas Backlund <tmb@mandriva.org>
#
# The mkflavour() macroization done by Anssi Hannula <anssi@mandriva.org>
#
# Note! remember to push kernel-userspace-headers and
# the prebuilt kernel drivers (kmod-<driver>)
#
# Mageia kernels use kernel.org versioning
#
%define kernelversion	4
%define patchlevel	12
# sublevel is now used for -stable patches
%define sublevel	14
# extstable is for extended stable patches
%define extstable	0

# Package release
%define mgarel		1

# kernel Makefile extraversion is substituted by
# kpatch which are either 0 (empty), rc (kpatch)
%define kpatch		0
# kernel.org -gitX patch (only the number after "git")
%define kgit		0

# kernel base name (also name of srpm)
%define kname 		kernel-unity

# Patch tarball tag
%define ktag		mga

%define rpmtag		%{distsuffix}%{mgaver}
%if %kpatch
%if %kgit
%define rpmrel		%mkrel 0.%{kpatch}.%{kgit}.%{mgarel}
%else
%define rpmrel		%mkrel 0.%{kpatch}.%{mgarel}
%endif
%else
%define rpmrel		%{mgarel}%{?dist}
%endif

# fakerel and fakever never change, they are used to fool
# rpm/urpmi/smart and ensure the kernels are installed,
# not upgraded so old kernel is not overwritten or removed
%define fakever		1
%define fakerel 	1%{?dist}

# version defines
%if %extstable
%define kversion  	%{kernelversion}.%{patchlevel}.%{sublevel}.%{extstable}
%else
%define kversion  	%{kernelversion}.%{patchlevel}.%{sublevel}
%endif
%define kverrel   	%{kversion}-%{rpmrel}

# When we are using a pre/rc patch, the tarball is a sublevel -1
%if %kpatch
%if %sublevel
%define tar_ver   	%{kernelversion}.%{patchlevel}
%else
%define tar_ver		%{kernelversion}.%(expr %{patchlevel} - 1)
%endif
%define patch_ver 	%{kversion}-%{kpatch}-%{ktag}%{mgarel}
%else
%define tar_ver   	%{kernelversion}.%{patchlevel}
%define patch_ver 	%{kversion}-%{ktag}%{mgarel}
%endif

# Used for not making too long names for rpms or search paths
%if %kpatch
%if %kgit
%define buildrpmrel     0.%{kpatch}.%{kgit}.%{mgarel}%{rpmtag}
%else
%define buildrpmrel     0.%{kpatch}.%{mgarel}%{rpmtag}
%endif
%else
%define buildrpmrel     %{mgarel}%{rpmtag}
%endif
%define buildrel     	%{kversion}-%{buildrpmrel}

# Having different top level names for packges means that you have to remove
# them by hard :(
%define top_dir_name 	%{kname}-%{_arch}

%define build_dir 	${RPM_BUILD_DIR}/%{top_dir_name}
%define src_dir 	%{build_dir}/linux-%{tar_ver}

# Disable useless debug rpms...
%global _enable_debug_packages	%{nil}
%global debug_package		%{nil}
%global __debug_package		%{nil}
%global __debug_install_post	%{nil}
%global _build_id_links none

# Build defines
%define build_doc 		1
%define build_source 		1
%define build_devel 		1

%define build_debug 		0

# Build desktop i586 / 4GB
%ifarch %{ix86}
%define build_desktop586	1
%endif

# Build desktop (i686 / 4GB) / x86_64
%define build_desktop		1

# Build server (i686 / 64GB)/x86_64 / sparc64 sets
%define build_server		0

# build perf and cpupower tools
%define build_perf		0
%define build_cpupower		1

# compress modules with xz
%define build_modxz		1

# ARM builds
%ifarch %{arm}
%define build_desktop		1
%ifarch armv5tl
%define build_desktop_armv6v7	1
%endif
%define build_server		0
%define build_iop32x		0
%define build_versatile		0
# no cpupower tools on arm yet
%define build_cpupower		0
# arm is currently not using xz
%define build_modxz		0
%endif
# End of user definitions

# buildtime flags
%{?_without_desktop586: %global build_desktop586 0}
%{?_without_desktop: %global build_desktop 0}
%{?_without_server: %global build_server 0}
%{?_without_doc: %global build_doc 0}
%{?_without_source: %global build_source 0}
%{?_without_devel: %global build_devel 0}
%{?_without_debug: %global build_debug 0}
%{?_without_perf: %global build_perf 0}
%{?_without_cpupower: %global build_cpupower 0}
%{?_without_modxz: %global build_modxz 0}

%{?_with_desktop586: %global build_desktop586 1}
%{?_with_desktop: %global build_desktop 1}
%{?_with_server: %global build_server 1}
%{?_with_doc: %global build_doc 1}
%{?_with_source: %global build_source 1}
%{?_with_devel: %global build_devel 1}
%{?_with_debug: %global build_debug 1}
%{?_with_perf: %global build_perf 1}
%{?_with_cpupower: %global build_cpupower 1}
%{?_with_modxz: %global build_modxz 1}

# ARM builds
%{?_with_iop32x: %global build_iop32x 1}
%{?_with_versatile: %global build_versatile 1}
%{?_without_iop32x: %global build_iop32x 0}
%{?_without_versatile: %global build_versatile 0}

# For the .nosrc.rpm
%define build_nosrc 	0
%{?_with_nosrc: %global build_nosrc 1}

%if %(if [ -z "$CC" ] ; then echo 0; else echo 1; fi)
%define kmake %make_build CC="$CC"
%else
%define kmake %make_build
%endif
# there are places where parallel make don't work
%define smake make

# Parallelize xargs invocations on smp machines
%define kxargs xargs %([ -z "$RPM_BUILD_NCPUS" ] \\\
	&& RPM_BUILD_NCPUS="`/usr/bin/getconf _NPROCESSORS_ONLN`"; \\\
	[ "$RPM_BUILD_NCPUS" -gt 1 ] && echo "-P $RPM_BUILD_NCPUS")

# Sparc arch wants sparc64 kernels
%define target_arch    %(echo %{_arch} | sed -e 's/mips.*/mips/' -e 's/arm.*/arm/')


#
# SRC RPM description
#
Summary: 	Linux kernel built for Mageia
Name:		%{kname}
Version: 	%{kversion}
Release: 	%{rpmrel}
License: 	GPLv2
Group: 	 	System/Kernel and hardware
ExclusiveArch: %{ix86} x86_64 %{arm}
ExclusiveOS: 	Linux
URL:            http://www.kernel.org

####################################################################
#
# Sources
#
### This is for full SRC RPM
Source0: 	https://cdn.kernel.org/pub/linux/kernel/v%{kernelversion}.x/linux-%{tar_ver}.tar.xz
Source1: 	https://cdn.kernel.org/pub/linux/kernel/v%{kernelversion}.x/linux-%{tar_ver}.tar.sign
### This is for stripped SRC RPM
%if %build_nosrc
NoSource: 0
%endif
# This is for disabling *config, mrproper, prepare, scripts on -devel rpms
Source2: 	disable-mrproper-prepare-scripts-configs-in-devel-rpms.patch

Source4: 	README.kernel-sources

# config and systemd service file from fedora
Source50:	cpupower.service
Source51:	cpupower.config

# our patch tarball
Source100: 	linux-%{patch_ver}.tar.xz

####################################################################
#
# Patches

#
# Patch0 to Patch100 are for core kernel upgrades.
#

# Pre linus patch: https://cdn.kernel.org/pub/linux/kernel/v3.0/testing

%if %kpatch
%if %sublevel
Patch2:		https://cdn.kernel.org/pub/linux/kernel/v%{kernelversion}.x/stable-review/patch-%{kversion}-%{kpatch}.xz
Source11:	https://cdn.kernel.org/pub/linux/kernel/v%{kernelversion}.x/stable-review/patch-%{kversion}-%{kpatch}.sign
%else
Patch1:		https://cdn.kernel.org/pub/linux/kernel/v%{kernelversion}.x/testing/patch-%{kernelversion}.%{patchlevel}-%{kpatch}.xz
Source10: 	https://cdn.kernel.org/pub/linux/kernel/v%{kernelversion}.x/testing/patch-%{kernelversion}.%{patchlevel}-%{kpatch}.sign
%endif
%endif
%if %kgit
Patch2:		https://cdn.kernel.org/pub/linux/kernel/v%{kernelversion}.x/snapshots/patch-%{kernelversion}.%{patchlevel}-%{kpatch}-git%{kgit}.xz
Source11: 	https://cdn.kernel.org/pub/linux/kernel/v%{kernelversion}.x/snapshots/patch-%{kernelversion}.%{patchlevel}-%{kpatch}-git%{kgit}.sign
%endif
%if %sublevel
%if %kpatch
%define prev_sublevel %(expr %{sublevel} - 1)
%if %prev_sublevel
Patch1:   	https://cdn.kernel.org/pub/linux/kernel/v%{kernelversion}.x/patch-%{kernelversion}.%{patchlevel}.%{prev_sublevel}.xz
Source10: 	https://cdn.kernel.org/pub/linux/kernel/v%{kernelversion}.x/patch-%{kernelversion}.%{patchlevel}.%{prev_sublevel}.sign
%endif
%else
Patch1:   	https://cdn.kernel.org/pub/linux/kernel/v%{kernelversion}.x/patch-%{kernelversion}.%{patchlevel}.%{sublevel}.xz
Source10: 	https://cdn.kernel.org/pub/linux/kernel/v%{kernelversion}.x/patch-%{kernelversion}.%{patchlevel}.%{sublevel}.sign
%endif
%endif
%if %extstable
Patch3:		patch-%{kernelversion}.%{patchlevel}.%{sublevel}.%{extstable}.patch
%endif

#END
####################################################################

# Defines for the things that are needed for all the kernels
#
%define common_desc_kernel The kernel package contains the Linux kernel (vmlinuz), the core of your \
Mageia operating system. The kernel handles the basic functions \
of the operating system: memory allocation, process allocation, device \
input and output, etc.

%define common_desc_kernel_smp This kernel relies on in-kernel smp alternatives to switch between up & smp \
mode depending on detected hardware. To force the kernel to boot in single \
processor mode, use the "nosmp" boot parameter.

### Global Requires/Provides
%define requires1	bootloader-utils >= 1.16-1
%define requires2	dracut >= 038-21
%define requires3	kmod >= 12-2
%define requires4	sysfsutils >= 2.1.0-16
%define requires5	kernel-firmware >= 20170101-1

%define kprovides1 	%{kname} = %{kverrel}
%define kprovides2 	kernel = %{tar_ver}
%define kprovides3 	kernel-desktop = %{tar_ver}
%define kprovides4 	alsa = 1.0.26
%define kprovides_server drbd-api = 88

# conflict dkms packages that dont support kernel-4.12
%define kconflicts1	dkms-broadcom-wl < 6.30.223.271-47
%define kconflicts2	dkms-fglrx <= 15.302
%define kconflicts3	dkms-nvidia-current < 375.82-1
%define kconflicts4	dkms-nvidia340 < 340.104-1
%define kconflicts5	dkms-nvidia304 < 304.137-1
%define kconflicts6	dkms-virtualbox < 5.1.26-1
%define kconflicts7	dkms-xtables-addons < 2.13-1
# (tmb) conflict older btrfs-progs to get the new in same transaction and in initrd
%define kconflicts8	btrfs-progs < 4.12-1
# (tmb) conflict too old radeon-firmware to get the uvd firmwares in initrd
%define kconflicts9	radeon-firmware < 20170101-1
# (tmb) conflict old firmware to get the firmwares in initrd
%define kconflicts10	kernel-firmware-nonfree < 20170101-1
# (tmb) conflict old microcode to get updated ones in initrd for early loading
%define kconflicts11	microcode < 0.20170707-1
# (tmb) conflict old theme to get mga5 theme in initrd
%define kconflicts12	mageia-gfxboot-theme < 4.5.6.6-1
# (tmb) conflict too old grub2(-efi)
%define kconflicts13	grub2 < 2.02-0.git9752.18
%define kconflicts14	grub2-efi < 2.02-0.git9752.18
# (tmb) conflict too old efibootmgr
%define kconflicts15	efibootmgr < 0.11.0-7
# (tmb) conflict for vmmouse breakage (for mga5, mga#16954)
%define kconflicts16	x11-driver-input-vmmouse < 13.1.0-1

Autoreqprov: 		no

BuildRequires: 		gcc >= 5.4.0-2
BuildRequires: 		binutils >= 1:2.24-0.20131016.1
BuildRequires: 		kmod >= 12-2
BuildRequires: 		bc
# for cpupower
%if %{build_cpupower}
BuildRequires:		pciutils-devel
%endif
# for perf
%if %{build_perf}
BuildRequires:		audit-devel
BuildRequires:		binutils-devel
BuildRequires:		elfutils-devel
BuildRequires:		gtk2-devel
BuildRequires:		libunwind-devel
BuildRequires:		newt-devel
BuildRequires:		python-devel
BuildRequires:		zlib-devel
BuildRequires:		asciidoc
BuildRequires:		bison
BuildRequires:		flex
BuildRequires:		xmlto
BuildRequires:		perl-devel
%ifarch %{ix86} x86_64
BuildRequires:		numa-devel
%endif
%endif


%description
%common_desc_kernel
%ifnarch %{arm}
%common_desc_kernel_smp
%endif

# mkflavour() name flavour processor
# name: the flavour name in the package name
# flavour: first parameter of CreateKernel()
%define mkflavour()					\
%package -n %{kname}-%{1}-%{buildrel}			\
Version:	%{fakever}				\
Release:	%{fakerel}				\
Provides:	%kprovides1 %kprovides2 %kprovides3  %kprovides4 \
%{expand:%%{?kprovides_%{1}:Provides: %{kprovides_%{1}}}} \
Provides:	%{kname}-%{1}				\
Provides:	kernel-%{1}				\
Requires(pre):	%requires1 %requires2 %requires3 %requires4 \
Requires:	%requires2 %requires5			\
Conflicts:	%kconflicts1 %kconflicts2 %kconflicts3	\
Conflicts:	%kconflicts4 %kconflicts5 %kconflicts6	\
Conflicts:	%kconflicts7 %kconflicts8 %kconflicts9	\
Conflicts:	%kconflicts10 %kconflicts11 %kconflicts12 \
Conflicts:	%kconflicts13 %kconflicts14 %kconflicts15 \
Conflicts:	%kconflicts16				\
Provides:	should-restart = system			\
Recommends:	crda iw cpupower			\
Recommends:	%{kname}-%{1}-latest			\
%ifarch %{ix86}						\
Conflicts:	arch(x86_64)				\
%endif							\
Summary:	%{expand:%{summary_%(echo %{1} | sed -e "s/-/_/")}} \
Group:		System/Kernel and hardware		\
%description -n %{kname}-%{1}-%{buildrel}		\
%common_desc_kernel %{expand:%{info_%(echo %{1} | sed -e "s/-/_/")}} \
%ifnarch %{arm}						\
%common_desc_kernel_smp					\
%endif							\
							\
%if %build_devel					\
%package -n	%{kname}-%{1}-devel-%{buildrel}		\
Version:	%{fakever}				\
Release:	%{fakerel}				\
Requires:	glibc-devel ncurses-devel make gcc perl	\
Summary:	The kernel-devel files for %{kname}-%{1}-%{buildrel} \
Group:		Development/Kernel			\
Provides:	%{kname}-devel = %{kverrel} 		\
Provides:	kernel-%{1}-devel			\
Provides:	%{kname}-%{1}-devel			\
Recommends:	kernel-%{1}-devel-latest		\
Recommends:	%{kname}-%{1}-devel-latest		\
%ifarch %{ix86}						\
Conflicts:	arch(x86_64)				\
%endif							\
%description -n %{kname}-%{1}-devel-%{buildrel}		\
This package contains the kernel files (headers and build tools) \
that should be enough to build additional drivers for   \
use with %{kname}-%{1}-%{buildrel}.                     \
							\
If you want to build your own kernel, you need to install the full \
%{kname}-source-%{buildrel} rpm.			\
							\
%endif							\
							\
%if %build_debug					\
%package -n	%{kname}-%{1}-%{buildrel}-debuginfo	\
Version:	%{fakever}				\
Release:	%{fakerel}				\
Summary:	Files with debuginfo for %{kname}-%{1}-%{buildrel} \
Group:		Development/Debug			\
Provides:	kernel-debug = %{kverrel} 		\
%ifarch %{ix86}						\
Conflicts:	arch(x86_64)				\
%endif							\
%description -n %{kname}-%{1}-%{buildrel}-debuginfo	\
This package contains the files with debuginfo to aid in debug tasks \
when using %{kname}-%{1}-%{buildrel}.			\
							\
If you need to look at debug information or use some application that \
needs debugging info from the kernel, this package may help. \
							\
%endif							\
							\
%package -n %{kname}-%{1}-latest			\
Version:	%{kversion}				\
Release:	%{rpmrel}				\
Summary:	Virtual rpm for latest %{kname}-%{1}	\
Group:		System/Kernel and hardware		\
Requires:	%{kname}-%{1}-%{buildrel}		\
%ifarch %{ix86}						\
Conflicts:	arch(x86_64)				\
%endif							\
%description -n %{kname}-%{1}-latest			\
This package is a virtual rpm that aims to make sure you always have the \
latest %{kname}-%{1} installed...			\
							\
%if %build_devel					\
%package -n %{kname}-%{1}-devel-latest			\
Version:	%{kversion}				\
Release:	%{rpmrel}				\
Summary:	Virtual rpm for latest %{kname}-%{1}-devel \
Group:		Development/Kernel			\
Requires:	%{kname}-%{1}-devel-%{buildrel}		\
%ifarch %{ix86}						\
Conflicts:	arch(x86_64)				\
%endif							\
Provides:	kernel-devel-latest			\
Provides:	%{kname}-devel-latest			\
%description -n %{kname}-%{1}-devel-latest		\
This package is a virtual rpm that aims to make sure you always have the \
latest %{kname}-%{1}-devel installed...			\
							\
%endif							\
							\
%posttrans -n %{kname}-%{1}-%{buildrel} -f kernel_files.%{1}-posttrans \
%preun -n %{kname}-%{1}-%{buildrel} -f kernel_files.%{1}-preun \
%postun -n %{kname}-%{1}-%{buildrel} -f kernel_files.%{1}-postun \
							\
%if %build_devel					\
%post -n %{kname}-%{1}-devel-%{buildrel} -f kernel_devel_files.%{1}-post \
%preun -n %{kname}-%{1}-devel-%{buildrel} -f kernel_devel_files.%{1}-preun \
%postun -n %{kname}-%{1}-devel-%{buildrel} -f kernel_devel_files.%{1}-postun \
%endif							\
							\
%files -n %{kname}-%{1}-%{buildrel} -f kernel_files.%{1} \
%files -n %{kname}-%{1}-latest				\
							\
%if %build_devel					\
%files -n %{kname}-%{1}-devel-%{buildrel} -f kernel_devel_files.%{1} \
%files -n %{kname}-%{1}-devel-latest			\
%endif							\
							\
%if %build_debug					\
%files -n %{kname}-%{1}-%{buildrel}-debuginfo -f kernel_debug_files.%{1} \
%endif

%ifarch %{ix86}
#
# kernel-desktop586: i586, smp-alternatives, 4GB
#
%if %build_desktop586
%define summary_desktop586 Linux kernel for desktop use with i586 and less than 4GB RAM
%define info_desktop586 This kernel is compiled for desktop use, single or \
multiple i586 processor(s)/core(s) and less than 4GB RAM (usually 3-3.5GB \
detected, if you need/want to use all 4GB or more, install kernel-server), \
using HZ_1000, voluntary preempt, CFS cpu scheduler and cfq i/o scheduler.
%mkflavour desktop586
%endif
%endif

#
# kernel-desktop: i686, smp-alternatives, 4 GB / x86_64
#
%if %build_desktop
%ifarch %{ix86}
%define summary_desktop Linux Kernel for desktop use with i686 and less than 4GB RAM
%define info_desktop This kernel is compiled for desktop use, single or \
multiple i686 processor(s)/core(s) and less than 4GB RAM (usually 3-3.5GB \
detected, if you need/want to use all 4GB or more, install kernel-server), \
using HZ_1000, voluntary preempt, CFS cpu scheduler and cfq i/o scheduler.
%else
%define summary_desktop Linux Kernel for desktop use with %{_arch}
%define info_desktop This kernel is compiled for desktop use, single or \
multiple %{_arch} processor(s)/core(s), using HZ_1000, voluntary preempt, \
CFS cpu scheduler and cfq i/o scheduler.
%endif
%mkflavour desktop
%endif

#
# kernel-server: i686, smp-alternatives, 64 GB / x86_64
#
%if %build_server
%ifarch %{ix86}
%define summary_server Linux Kernel for server use with i686 & 64GB RAM
%define info_server This kernel is compiled for server use, single or \
multiple i686 processor(s)/core(s) and up to 64GB RAM using PAE, using \
no preempt, HZ_100, CFS cpu scheduler and cfq i/o scheduler.
%else
%define summary_server Linux Kernel for server use with %{_arch}
%define info_server This kernel is compiled for server use, single or \
multiple %{_arch} processor(s)/core(s), using no preempt, HZ_100, \
CFS cpu scheduler and cfq i/o scheduler.
%endif
%mkflavour server
%endif

#
# ARM kernels
#
%ifarch armv5tl
#
# kernel-desktop-armv6v7
#
%if %build_desktop_armv6v7
%define summary_desktop_armv6v7 Linux kernel for desktop use with ARMv6 or ARMv7
%define info_desktop_armv6v7 This kernel is compiled for desktop use, single or \
multiple ARMv6 or ARMv7 processor(s)/core(s), using HZ_1000, voluntary preempt, \
CFS cpu scheduler and cfq i/o scheduler.
%mkflavour desktop-armv6v7
%endif
%endif
%ifarch %{arm}
%if %build_iop32x
%define summary_iop32x Linux Kernel for Arm machines based on Xscale IOP32X
%define info_iop32x This kernel is compiled for iop32x boxes. It will run on n2100 \
or ss4000e or sanmina boards.
%mkflavour iop32x
%endif
%if %build_versatile
%define summary_versatile Linux Kernel for Versatile arm machines
%define info_versatile This kernel is compiled for Versatile boxes. It will run on Qemu for instance.
%mkflavour versatile
%endif
%endif

#
# kernel-source
#
%if %build_source
%package -n %{kname}-source-%{buildrel}
Version: 	%{fakever}
Release: 	%{fakerel}
Requires: 	glibc-devel, ncurses-devel, make, gcc, perl, diffutils
Summary: 	The Linux source code for %{kname}-%{buildrel}
Group: 		Development/Kernel
Autoreqprov: 	no
Provides: 	kernel-source = %{kverrel}
Buildarch:	noarch

%description -n %{kname}-source-%{buildrel}
The %{kname}-source package contains the source code files for the Mageia
kernel. Theese source files are only needed if you want to build your
own custom kernel that is better tuned to your particular hardware.

If you only want the files needed to build 3rdparty (nVidia, Ati, dkms-*,...)
drivers against, install the *-devel-* rpm that is matching your kernel.

#
# kernel-source-latest: virtual rpm
#
%package -n %{kname}-source-latest
Version: 	%{kversion}
Release: 	%{rpmrel}
Summary: 	Virtual rpm for latest %{kname}-source
Group:   	Development/Kernel
Requires: 	%{kname}-source-%{buildrel}
Buildarch:	noarch

%description -n %{kname}-source-latest
This package is a virtual rpm that aims to make sure you always have the
latest %{kname}-source installed...
%endif

#
# kernel-doc: documentation for the Linux kernel
#
%if %build_doc
%package -n %{kname}-doc
Version: 	%{kversion}
Release: 	%{rpmrel}
Summary: 	Various documentation bits found in the %{kname} source
Group: 		Documentation
Buildarch:	noarch

%description -n %{kname}-doc
This package contains documentation files from the %{kname} source.
Various bits of information about the Linux kernel and the device drivers
shipped with it are documented in these files. You also might want install
this package if you need a reference to the options that can be passed to
Linux kernel modules at load time.
%endif

#
# kernel/tools
#
%if %{build_perf}
%package -n perf
Version:	%{kversion}
Release:	%{rpmrel}
Summary:	perf tool and the supporting documentation
Group:		System/Kernel and hardware

%description -n perf
the perf tool and the supporting documentation.
%endif

%if %{build_cpupower}
%package -n cpupower
Version:	%{kversion}
Release:	%{rpmrel}
Summary:	the cpupower tools
Group:		System/Kernel and hardware
Requires(post):  rpm-helper >= 0.24.8-1
Requires(preun): rpm-helper >= 0.24.8-1
Obsoletes:	cpufreq cpufrequtils

%description -n cpupower
the cpupower tools.

%post -n cpupower
%_post_service cpupower

%preun -n cpupower
%_preun_service cpupower

%package -n cpupower-devel
Version:	%{kversion}
Release:	%{rpmrel}
Summary:	devel files for cpupower
Group:		Development/Kernel
Requires:	cpupower = %{kversion}-%{rpmrel}
Conflicts:	%{_lib}cpufreq-devel

%description -n cpupower-devel
This package contains the development files for cpupower.
%endif


#
# End packages - here begins build stage
#
%prep
%setup -q -n %top_dir_name -c
%setup -q -n %top_dir_name -D -T -a100

%define patches_dir ../%{patch_ver}/

cd %src_dir

%if %sublevel
%if %kpatch
%if %prev_sublevel
%patch1 -p1
%endif
%patch2 -p1
%else
%patch1 -p1
%endif
%else
%if %kpatch
# (tmb) hack around rpm patch hiccup
xzcat %{PATCH1}| patch -p1 ||:
%endif
%endif
%if %kgit
%patch2 -p1
%endif
%if %extstable
%patch3 -p1
%endif

%{patches_dir}/scripts/apply_patches

# PATCH END


#
# Setup Begin
#

# Prepare all the variables for calling create_configs

%if %build_debug
%define debug --debug
%else
%define debug --no-debug
%endif


%{patches_dir}/scripts/create_configs %debug --user_cpu="%{target_arch}"

# make sure the kernel has the sublevel we know it has...
LC_ALL=C perl -p -i -e "s/^SUBLEVEL.*/SUBLEVEL = %{sublevel}/" Makefile

# get rid of unwanted files
find . -name '*~' -o -name '*.orig' -o -name '*.append' | %kxargs rm -f


%build
# Common target directories
%define _kerneldir /usr/src/kernel-%{kversion}-%{buildrpmrel}
%define _bootdir /boot
%define _modulesdir /lib/modules
%define _efidir %{_bootdir}/efi/mageia

# Directories definition needed for building
%define temp_root %{build_dir}/temp-root
%define temp_source %{temp_root}%{_kerneldir}
%define temp_boot %{temp_root}%{_bootdir}
%define temp_modules %{temp_root}%{_modulesdir}

PrepareKernel() {
	name=$1
	extension=$2
	x86_dir=arch/x86/configs

	echo "Make config for kernel $extension"

	%smake -s mrproper

	if [ "%{target_arch}" == "i386" -o "%{target_arch}" == "x86_64" ]; then
	    if [ -z "$name" ]; then
		cp ${x86_dir}/%{target_arch}_defconfig-desktop .config
	    else
		cp ${x86_dir}/%{target_arch}_defconfig-$name .config
	    fi
	else
	    if [ -z "$name" ]; then
		cp arch/%{target_arch}/defconfig-desktop .config
	    else
		cp arch/%{target_arch}/defconfig-$name .config
	    fi
	fi

	# make sure EXTRAVERSION says what we want it to say
	%if %extstable
	LC_ALL=C perl -p -i -e "s/^EXTRAVERSION.*/EXTRAVERSION = .%{extstable}-$extension/" Makefile
	%else
	LC_ALL=C perl -p -i -e "s/^EXTRAVERSION.*/EXTRAVERSION = -$extension/" Makefile
	%endif

	%smake oldconfig
}

BuildKernel() {
	KernelVer=$1

	echo "Building kernel $KernelVer"

	%kmake -s all

	# Start installing stuff
	install -d %{temp_boot}
	install -m 644 System.map %{temp_boot}/System.map-$KernelVer
	install -m 644 .config %{temp_boot}/config-$KernelVer
	xz -c Module.symvers > %{temp_boot}/symvers-$KernelVer.xz

	%ifarch %{arm}
		cp -f arch/arm/boot/zImage %{temp_boot}/vmlinuz-$KernelVer
		install -d %{temp_root}/usr/lib/linux-$KernelVer/
		for d in arch/arm/boot/dts/*.dtb; do \
			install -D -m644 $d %{temp_root}/usr/lib/linux-$KernelVer/$(basename $d); \
		done
	%else
		cp -f arch/%{target_arch}/boot/bzImage %{temp_boot}/vmlinuz-$KernelVer
	%endif

	# modules
	install -d %{temp_modules}/$KernelVer
	%smake INSTALL_MOD_PATH=%{temp_root} KERNELRELEASE=$KernelVer modules_install

	# remove /lib/firmware, we use a separate kernel-firmware
	rm -rf %{temp_root}/lib/firmware
}

SaveDevel() {
	devel_flavour=$1

	DevelRoot=/usr/src/kernel-%{kversion}-$devel_flavour-%{buildrpmrel}
	TempDevelRoot=%{temp_root}$DevelRoot

	mkdir -p $TempDevelRoot
	for i in $(find . -name 'Makefile*'); do cp -R --parents $i $TempDevelRoot;done
	for i in $(find . -name 'Kconfig*' -o -name 'Kbuild*'); do cp -R --parents $i $TempDevelRoot;done
	cp -fR include $TempDevelRoot
	cp -fR scripts $TempDevelRoot
	cp -fR kernel/bounds.c $TempDevelRoot/kernel
	cp -fR tools/include $TempDevelRoot/tools/
	%ifarch %{arm}
		cp -fR arch/%{target_arch}/tools $TempDevelRoot/arch/%{target_arch}/
	%endif
	%ifarch %{ix86} x86_64
		cp -fR arch/x86/kernel/asm-offsets.{c,s} $TempDevelRoot/arch/x86/kernel/
		cp -fR arch/x86/kernel/asm-offsets_{32,64}.c $TempDevelRoot/arch/x86/kernel/
		cp -fR arch/x86/purgatory/* $TempDevelRoot/arch/x86/purgatory/
		cp -fR arch/x86/entry/syscalls/syscall* $TempDevelRoot/arch/x86/entry/syscalls/
		cp -fR arch/x86/include $TempDevelRoot/arch/x86/
		cp -fR arch/x86/tools $TempDevelRoot/arch/x86/
	%else
		cp -fR arch/%{target_arch}/kernel/asm-offsets.{c,s} $TempDevelRoot/arch/%{target_arch}/kernel/
		for f in $(find arch/%{target_arch} -name include); do cp -fR --parents $f $TempDevelRoot; done
	%endif
	cp -fR .config Module.symvers $TempDevelRoot
	cp -fR 3rdparty/mkbuild.pl $TempDevelRoot/3rdparty

	# Needed for truecrypt build (Danny)
	cp -fR drivers/md/dm.h $TempDevelRoot/drivers/md/

	# needed by include/generated/timeconst.h
	cp -fR kernel/time/timeconst.bc $TempDevelRoot/kernel/time/

	# Needed for lguest
	cp -fR drivers/lguest/lg.h $TempDevelRoot/drivers/lguest/

	# Needed for lirc_gpio (#39004)
	cp -fR drivers/media/pci/bt8xx/bttv{,p}.h $TempDevelRoot/drivers/media/pci/bt8xx/
	cp -fR drivers/media/pci/bt8xx/bt848.h $TempDevelRoot/drivers/media/pci/bt8xx/
	cp -fR drivers/media/common/btcx-risc.h $TempDevelRoot/drivers/media/common/

	# Needed for external dvb tree (#41418)
	cp -fR drivers/media/dvb-core/*.h $TempDevelRoot/drivers/media/dvb-core/
	cp -fR drivers/media/dvb-frontends/lgdt330x.h $TempDevelRoot/drivers/media/dvb-frontends/

	# add acpica header files, needed for fglrx build
	cp -fR drivers/acpi/acpica/*.h $TempDevelRoot/drivers/acpi/acpica/

	# aufs2 has a special file needed
	cp -fR fs/aufs/magic.mk $TempDevelRoot/fs/aufs

	for i in alpha arc avr32 blackfin c6x cris frv h8300 hexagon ia64 m32r m68k m68knommu metag microblaze \
		 mips mn10300 nios2 openrisc parisc powerpc s390 score sh sparc tile unicore32 xtensa; do
		rm -rf $TempDevelRoot/arch/$i
		rm -rf $TempDevelRoot/tools/arch/$i
	done

	%ifnarch %{arm}
		rm -rf $TempDevelRoot/arch/arm*
		rm -rf $TempDevelRoot/include/kvm/arm*
		rm -rf $TempDevelRoot/include/soc
		rm -rf $TempDevelRoot/tools/arch/arm*
	%endif
	%ifnarch %{ix86} x86_64
		rm -rf $TempDevelRoot/arch/x86
		rm -rf $TempDevelRoot/tools/arch/x86
		# arch/x86/ras/Kconfig is included by drivers/ras/Kconfig
		# and kconfig's source command seems to be evaluated even under a false conditional
		mkdir -p $TempDevelRoot/arch/x86/ras
		cp -fR arch/x86/ras/{Kconfig,Makefile} $TempDevelRoot/arch/x86/ras
	%endif

	# Clean the scripts tree, and make sure everything is ok (sanity check)
	# running prepare+scripts (tree was already "prepared" in build)
	pushd $TempDevelRoot >/dev/null
		%smake -s prepare scripts
		%smake -s clean
	popd >/dev/null
	rm -f $TempDevelRoot/.config.old

	# fix permissions
	chmod -R a+rX $TempDevelRoot

	# disable mrproper in -devel rpms
	patch -p1 --fuzz=0 -d $TempDevelRoot -i %{SOURCE2}

	kernel_devel_files=../kernel_devel_files.$devel_flavour


### Create the kernel_devel_files.*
cat > $kernel_devel_files <<EOF
%dir $DevelRoot
%dir $DevelRoot/arch
%dir $DevelRoot/include
$DevelRoot/3rdparty
$DevelRoot/Documentation
%ifarch %{arm}
$DevelRoot/arch/arm
$DevelRoot/arch/arm64
%endif
$DevelRoot/arch/um
%ifarch %{ix86} x86_64
$DevelRoot/arch/x86
%else
$DevelRoot/arch/x86/ras
%endif
$DevelRoot/block
$DevelRoot/certs
$DevelRoot/crypto
$DevelRoot/drivers
$DevelRoot/firmware
$DevelRoot/fs
$DevelRoot/include/acpi
$DevelRoot/include/asm-generic
$DevelRoot/include/clocksource
$DevelRoot/include/config
$DevelRoot/include/crypto
$DevelRoot/include/drm
$DevelRoot/include/dt-bindings
$DevelRoot/include/generated
$DevelRoot/include/keys
$DevelRoot/include/kvm
$DevelRoot/include/linux
$DevelRoot/include/math-emu
$DevelRoot/include/media
$DevelRoot/include/memory
$DevelRoot/include/misc
$DevelRoot/include/net
$DevelRoot/include/pcmcia
$DevelRoot/include/ras
$DevelRoot/include/rdma
$DevelRoot/include/rxrpc
$DevelRoot/include/scsi
%ifarch %{arm}
$DevelRoot/include/soc
%endif
$DevelRoot/include/sound
$DevelRoot/include/target
$DevelRoot/include/trace
$DevelRoot/include/uapi
$DevelRoot/include/video
$DevelRoot/include/xen
$DevelRoot/init
$DevelRoot/ipc
$DevelRoot/kernel
$DevelRoot/lib
$DevelRoot/mm
$DevelRoot/net
$DevelRoot/samples
$DevelRoot/scripts
$DevelRoot/security
$DevelRoot/sound
$DevelRoot/tools
$DevelRoot/usr
$DevelRoot/virt
$DevelRoot/.config
$DevelRoot/Kbuild
$DevelRoot/Kconfig
$DevelRoot/Makefile
$DevelRoot/Module.symvers
$DevelRoot/arch/Kconfig
%doc README.kernel-sources
EOF


### Create -devel Post script on the fly
cat > $kernel_devel_files-post <<EOF
if [ -d /lib/modules/%{kversion}-$devel_flavour-%{buildrpmrel} ]; then
	rm -f /lib/modules/%{kversion}-$devel_flavour-%{buildrpmrel}/{build,source}
	ln -sf $DevelRoot /lib/modules/%{kversion}-$devel_flavour-%{buildrpmrel}/build
	ln -sf $DevelRoot /lib/modules/%{kversion}-$devel_flavour-%{buildrpmrel}/source
fi
EOF


### Create -devel Preun script on the fly
cat > $kernel_devel_files-preun <<EOF
if [ -L /lib/modules/%{kversion}-$devel_flavour-%{buildrpmrel}/build ]; then
	rm -f /lib/modules/%{kversion}-$devel_flavour-%{buildrpmrel}/build
fi
if [ -L /lib/modules/%{kversion}-$devel_flavour-%{buildrpmrel}/source ]; then
	rm -f /lib/modules/%{kversion}-$devel_flavour-%{buildrpmrel}/source
fi
exit 0
EOF

### Create -devel Postun script on the fly
cat > $kernel_devel_files-postun <<EOF
rm -rf /usr/src/kernel-%{kversion}-$devel_flavour-%{buildrpmrel} >/dev/null
EOF
}

SaveDebug() {
	debug_flavour=$1

	install -m 644 vmlinux \
	      %{temp_boot}/vmlinux-%{kversion}-$debug_flavour-%{buildrpmrel}
	kernel_debug_files=../kernel_debug_files.$debug_flavour
	echo "%{_bootdir}/vmlinux-%{kversion}-$debug_flavour-%{buildrpmrel}" \
		>> $kernel_debug_files

	find %{temp_modules}/%{kversion}-$debug_flavour-%{buildrpmrel}/kernel \
		-name "*.ko" | \
		%kxargs -I '{}' objcopy --only-keep-debug '{}' '{}'.debug
	find %{temp_modules}/%{kversion}-$debug_flavour-%{buildrpmrel}/kernel \
		-name "*.ko" | %kxargs -I '{}' \
		sh -c 'cd `dirname {}`; \
		       objcopy --add-gnu-debuglink=`basename {}`.debug \
		       --strip-debug `basename {}`'

	pushd %{temp_modules}
	find %{kversion}-$debug_flavour-%{buildrpmrel}/kernel \
		-name "*.ko.debug" > debug_module_list
	popd
	cat %{temp_modules}/debug_module_list | \
		sed 's|\(.*\)|%{_modulesdir}/\1|' >> $kernel_debug_files
	cat %{temp_modules}/debug_module_list | \
		sed 's|\(.*\)|%exclude %{_modulesdir}/\1|' \
		>> ../kernel_exclude_debug_files.$debug_flavour
	rm -f %{temp_modules}/debug_module_list
}

CreateFiles() {
	kernel_flavour=$1

	kernel_files=../kernel_files.$kernel_flavour

ker="vmlinuz"
### Create the kernel_files.*
cat > $kernel_files <<EOF
%{_bootdir}/System.map-%{kversion}-$kernel_flavour-%{buildrpmrel}
%{_bootdir}/symvers-%{kversion}-$kernel_flavour-%{buildrpmrel}.xz
%{_bootdir}/config-%{kversion}-$kernel_flavour-%{buildrpmrel}
%{_bootdir}/$ker-%{kversion}-$kernel_flavour-%{buildrpmrel}
%dir %{_modulesdir}/%{kversion}-$kernel_flavour-%{buildrpmrel}/
%{_modulesdir}/%{kversion}-$kernel_flavour-%{buildrpmrel}/kernel
%{_modulesdir}/%{kversion}-$kernel_flavour-%{buildrpmrel}/modules.*
%doc README.kernel-sources
%ifarch %arm
%dir /usr/lib/linux-%{kversion}-$kernel_flavour-%{buildrpmrel}
/usr/lib/linux-%{kversion}-$kernel_flavour-%{buildrpmrel}/*.dtb
%endif
EOF

%if %build_debug
    cat ../kernel_exclude_debug_files.$kernel_flavour >> $kernel_files
%endif

### Create kernel Posttrans script
cat > $kernel_files-posttrans <<EOF
%if %build_devel
# create kernel-devel symlinks if matching -devel- rpm is installed
if [ -d /usr/src/kernel-%{kversion}-$kernel_flavour-%{buildrpmrel} ]; then
	rm -f /lib/modules/%{kversion}-$kernel_flavour-%{buildrpmrel}/{build,source}
	ln -sf /usr/src/kernel-%{kversion}-$kernel_flavour-%{buildrpmrel} /lib/modules/%{kversion}-$kernel_flavour-%{buildrpmrel}/build
	ln -sf /usr/src/kernel-%{kversion}-$kernel_flavour-%{buildrpmrel} /lib/modules/%{kversion}-$kernel_flavour-%{buildrpmrel}/source
fi
%endif
if [ -z "$DURING_INSTALL" ] ; then
    if [ -x /usr/sbin/dkms_autoinstaller -a -d /usr/src/kernel-%{kversion}-$kernel_flavour-%{buildrpmrel} ]; then
	/usr/sbin/dkms_autoinstaller start %{kversion}-$kernel_flavour-%{buildrpmrel}
    fi
fi
%ifarch %{arm}
/sbin/installkernel -i -N %{kversion}-$kernel_flavour-%{buildrpmrel}
%else
/sbin/installkernel %{kversion}-$kernel_flavour-%{buildrpmrel}
pushd /boot > /dev/null
if [ -e initrd-%{kversion}-$kernel_flavour-%{buildrpmrel}.img ]; then
	if [ -L vmlinuz-$kernel_flavour ]; then
		rm -f vmlinuz-$kernel_flavour
	fi
	ln -sf vmlinuz-%{kversion}-$kernel_flavour-%{buildrpmrel} vmlinuz-$kernel_flavour
	ln -sf vmlinuz-%{kversion}-$kernel_flavour-%{buildrpmrel} vmlinuz
	if [ -L initrd-$kernel_flavour.img ]; then
		rm -f initrd-$kernel_flavour.img
	fi
	ln -sf initrd-%{kversion}-$kernel_flavour-%{buildrpmrel}.img initrd-$kernel_flavour.img
	ln -sf initrd-%{kversion}-$kernel_flavour-%{buildrpmrel}.img initrd.img
fi
popd > /dev/null
%endif
EOF

### Create kernel Preun script on the fly
cat > $kernel_files-preun <<EOF
/sbin/installkernel -R %{kversion}-$kernel_flavour-%{buildrpmrel}
pushd /boot > /dev/null
if [ -L vmlinuz-$kernel_flavour ]; then
	if [ "$(readlink vmlinuz-$kernel_flavour)" = "vmlinuz-%{kversion}-$kernel_flavour-%{buildrpmrel}" ]; then
		rm -f vmlinuz-$kernel_flavour
	fi
fi
if [ -L initrd-$kernel_flavour.img ]; then
	if [ "$(readlink initrd-$kernel_flavour.img)" = "initrd-%{kversion}-$kernel_flavour-%{buildrpmrel}.img" ]; then
		rm -f initrd-$kernel_flavour.img
	fi
fi
popd > /dev/null
%if %build_devel
if [ -L /lib/modules/%{kversion}-$kernel_flavour-%{buildrpmrel}/build ]; then
	rm -f /lib/modules/%{kversion}-$kernel_flavour-%{buildrpmrel}/build
fi
if [ -L /lib/modules/%{kversion}-$kernel_flavour-%{buildrpmrel}/source ]; then
	rm -f /lib/modules/%{kversion}-$kernel_flavour-%{buildrpmrel}/source
fi
%endif
exit 0
EOF


### Create kernel Postun script on the fly
cat > $kernel_files-postun <<EOF
/sbin/kernel_remove_initrd %{kversion}-$kernel_flavour-%{buildrpmrel}
rm -rf /lib/modules/%{kversion}-$kernel_flavour-%{buildrpmrel} >/dev/null
if [ -d /var/lib/dkms ]; then
    rm -f /var/lib/dkms/*/kernel-%{kversion}-$devel_flavour-%{buildrpmrel}-%{_target_cpu} >/dev/null
    rm -rf /var/lib/dkms/*/*/%{kversion}-$devel_flavour-%{buildrpmrel} >/dev/null
    rm -f /var/lib/dkms-binary/*/kernel-%{kversion}-$devel_flavour-%{buildrpmrel}-%{_target_cpu} >/dev/null
    rm -rf /var/lib/dkms-binary/*/*/%{kversion}-$devel_flavour-%{buildrpmrel} >/dev/null
fi
EOF
}


CreateKernel() {
	flavour=$1

	PrepareKernel $flavour $flavour-%{buildrpmrel}

	BuildKernel %{kversion}-$flavour-%{buildrpmrel}
	%if %build_devel
		SaveDevel $flavour
	%endif
	%if %build_debug
		SaveDebug $flavour
	%endif
	CreateFiles $flavour
}


###
# DO it...
###


# Create a simulacro of buildroot
rm -rf %{temp_root}
install -d %{temp_root}


# make sure we are in the directory
cd %src_dir

%ifarch %{ix86}
%if %build_desktop586
CreateKernel desktop586
%endif
%endif

%if %build_desktop
CreateKernel desktop
%endif

%if %build_server
CreateKernel server
%endif

%ifarch armv5tl
%if %build_desktop_armv6v7
CreateKernel desktop-armv6v7
%endif
%endif

%ifarch %{arm}
%if %build_iop32x
CreateKernel iop32x
%endif
%if %build_versatile
CreateKernel versatile
%endif
%endif

# set extraversion to match srpm to get nice version reported by the tools
%if %extstable
LC_ALL=C perl -p -i -e "s/^EXTRAVERSION.*/EXTRAVERSION = .%{extstable}-%{rpmrel}/" Makefile
%else
LC_ALL=C perl -p -i -e "s/^EXTRAVERSION.*/EXTRAVERSION = -%{rpmrel}/" Makefile
%endif
# build perf
%if %{build_perf}
# perf
%smake -C tools/perf -s HAVE_CPLUS_DEMANGLE=1 prefix=%{_prefix} all
%smake -C tools/perf -s prefix=%{_prefix} man
%endif

%if %{build_cpupower}
# cpupower
# make sure version-gen.sh is executable.
chmod +x tools/power/cpupower/utils/version-gen.sh
%make_build -C tools/power/cpupower CPUFREQ_BENCH=false
%endif

# We don't make to repeat the depend code at the install phase
%if %build_source
PrepareKernel "" %{buildrpmrel}custom
%smake -s mrproper
%endif


###
### install
###
%install
install -m 644 %{SOURCE4}  .

cd %src_dir

# Directories definition needed for installing
%define target_source %{buildroot}%{_kerneldir}
%define target_boot %{buildroot}%{_bootdir}
%define target_modules %{buildroot}%{_modulesdir}

# We want to be able to test several times the install part
rm -rf %{buildroot}
cp -a %{temp_root} %{buildroot}

# Create directories infastructure
%if %build_source
install -d %{target_source}

tar cf - . | tar xf - -C %{target_source}
chmod -R a+rX %{target_source}

# we remove all the source files that we don't ship
# first architecture files
for i in alpha arc avr32 blackfin c6x cris frv h8300 hexagon ia64 m32r m68k m68knommu metag microblaze \
	 mips nios2 openrisc parisc powerpc s390 score sh sh64 sparc tile unicore32 v850 xtensa mn10300; do
	rm -rf %{target_source}/arch/$i
	rm -rf %{target_source}/tools/arch/$i
	rm -rf %{target_source}/tools/testing/selftests/$i
done
%ifnarch %{arm}
	rm -rf %{target_source}/include/kvm/arm*
	rm -rf %{target_source}/tools/arch/arm*
%endif

# other misc files
rm -f %{target_source}/{.config.old,.config.cmd,.lst,.mailmap,.get_maintainer.ignore}
rm -f %{target_source}/{.missing-syscalls.d,.cocciconfig,.gitattributes}
rm -rf %{target_source}/.tmp_depmod/

# more cleaning
pushd %{target_source}
# lots of gitignore files
find -iname ".gitignore" -delete
# clean tools tree
%smake -C tools clean
%smake -C tools/build clean
%smake -C tools/build/feature clean
popd

#endif %build_source
%endif

# compressing modules
%if %{build_modxz}
find %{target_modules} -name "*.ko" | %kxargs xz -6e
%else
find %{target_modules} -name "*.ko" | %kxargs gzip -9
%endif

# We used to have a copy of PrepareKernel here
# Now, we make sure that the thing in the linux dir is what we want it to be
for i in %{target_modules}/*; do
	rm -f $i/build $i/source
done

# sniff, if we compressed all the modules, we change the stamp :(
# we really need the depmod -ae here
pushd %{target_modules}
for i in *; do
	/sbin/depmod -ae -b %{buildroot} -F %{target_boot}/System.map-$i $i
	echo $?
done

for i in *; do
	pushd $i
	echo "Creating modules.description for $i"
	modules=`find . -name "*.ko.[g,x]z"`
	echo $modules | %kxargs /sbin/modinfo \
	| perl -lne 'print "$name\t$1" if $name && /^description:\s*(.*)/; $name = $1 if m!^filename:\s*(.*)\.k?o!; $name =~ s!.*/!!' > modules.description
	popd
done
popd

# need to set extraversion to match srpm again to avoid rebuild
%if %extstable
LC_ALL=C perl -p -i -e "s/^EXTRAVERSION.*/EXTRAVERSION = .%{extstable}-%{rpmrel}/" Makefile
%else
LC_ALL=C perl -p -i -e "s/^EXTRAVERSION.*/EXTRAVERSION = -%{rpmrel}/" Makefile
%endif
%if %{build_perf}
# perf tool binary and supporting scripts/binaries
make -C tools/perf V=1 DESTDIR=%{buildroot} HAVE_CPLUS_DEMANGLE=1 prefix=%{_prefix} install

# perf man pages (note: implicit rpm magic compresses them later)
make -C tools/perf V=1 DESTDIR=%{buildroot} HAVE_CPLUS_DEMANGLE=1 prefix=%{_prefix} install-man
%endif

%if %{build_cpupower}
make -C tools/power/cpupower DESTDIR=%{buildroot} libdir=%{_libdir} mandir=%{_mandir} CPUFREQ_BENCH=false install
rm -f %{buildroot}%{_libdir}/*.{a,la}
%find_lang cpupower
mv cpupower.lang ../
chmod 0755 %{buildroot}%{_libdir}/libcpupower.so*
mkdir -p %{buildroot}%{_unitdir} %{buildroot}%{_sysconfdir}/sysconfig
install -m644 %{SOURCE50} %{buildroot}%{_unitdir}/cpupower.service
install -m644 %{SOURCE51} %{buildroot}%{_sysconfdir}/sysconfig/cpupower
%endif

###
### clean
###
%clean
rm -rf %{buildroot}


# We don't want to remove this, the whole reason of its existence is to be
# able to do several rpm --short-circuit -bi for testing install
# phase without repeating compilation phase
#rm -rf %{temp_root}

###
### source and doc file lists
###

%if %build_source
%files -n %{kname}-source-%{buildrel}
%dir %{_kerneldir}
%dir %{_kerneldir}/arch
%dir %{_kerneldir}/include
%{_kerneldir}/3rdparty
%{_kerneldir}/Documentation
%{_kerneldir}/arch/Kconfig
%{_kerneldir}/arch/arm
%{_kerneldir}/arch/arm64
%{_kerneldir}/arch/um
%{_kerneldir}/arch/x86
%{_kerneldir}/block
%{_kerneldir}/certs
%{_kerneldir}/crypto
%{_kerneldir}/drivers
%{_kerneldir}/firmware
%{_kerneldir}/fs
%{_kerneldir}/include/acpi
%{_kerneldir}/include/asm-generic
%{_kerneldir}/include/clocksource
%{_kerneldir}/include/crypto
%{_kerneldir}/include/drm
%{_kerneldir}/include/dt-bindings
%{_kerneldir}/include/keys
%{_kerneldir}/include/kvm
%{_kerneldir}/include/linux
%{_kerneldir}/include/math-emu
%{_kerneldir}/include/media
%{_kerneldir}/include/memory
%{_kerneldir}/include/misc
%{_kerneldir}/include/net
%{_kerneldir}/include/pcmcia
%{_kerneldir}/include/ras
%{_kerneldir}/include/rdma
%{_kerneldir}/include/rxrpc
%{_kerneldir}/include/scsi
%{_kerneldir}/include/soc
%{_kerneldir}/include/sound
%{_kerneldir}/include/target
%{_kerneldir}/include/trace
%{_kerneldir}/include/uapi
%{_kerneldir}/include/video
%{_kerneldir}/include/xen
%{_kerneldir}/init
%{_kerneldir}/ipc
%{_kerneldir}/kernel
%{_kerneldir}/lib
%{_kerneldir}/mm
%{_kerneldir}/net
%{_kerneldir}/virt
%{_kerneldir}/samples
%{_kerneldir}/scripts
%{_kerneldir}/security
%{_kerneldir}/sound
%{_kerneldir}/tools
%{_kerneldir}/usr
%{_kerneldir}/COPYING
%{_kerneldir}/CREDITS
%{_kerneldir}/Kbuild
%{_kerneldir}/Kconfig
%{_kerneldir}/MAINTAINERS
%{_kerneldir}/Makefile
%{_kerneldir}/README
%doc README.kernel-sources

%files -n %{kname}-source-latest
%endif

%if %build_doc
%files -n %{kname}-doc
%doc linux-%{tar_ver}/Documentation/*
%endif

%if %{build_perf}
%files -n perf
%{_bindir}/perf
%ifarch x86_64
%{_bindir}/perf-read-vdso32
%endif
%{_bindir}/trace
%{_libdir}/libperf-gtk.so
%{_datadir}/perf-core/strace/groups/file
%{_datadir}/doc/perf-tip/tips.txt
%dir %{_libdir}/traceevent
%dir %{_libdir}/traceevent/plugins
%{_libdir}/traceevent/plugins/plugin_*
%dir %{_prefix}/libexec/perf-core
%{_prefix}/libexec/perf-core/*
%{_mandir}/man[1-8]/perf*
%{_sysconfdir}/bash_completion.d/perf
%endif

%if %{build_cpupower}
%files -n cpupower -f cpupower.lang
%{_bindir}/cpupower
%{_libdir}/libcpupower.so.0
%{_libdir}/libcpupower.so.0.0.1
%{_unitdir}/cpupower.service
%{_mandir}/man[1-8]/cpupower*
%config(noreplace) %{_sysconfdir}/sysconfig/cpupower

%files -n cpupower-devel
%{_libdir}/libcpupower.so
%{_includedir}/cpuidle.h
%{_includedir}/cpufreq.h
%endif


%changelog
* Sun Aug 13 2017 tmb <tmb> 4.12.7-1.mga7
+ Revision: 1140056
- update to 4.12.7 final

* Sat Aug 12 2017 tmb <tmb> 4.12.6-1.mga7
+ Revision: 1139925
- add 4.12.7-rc1
- update to 4.12.6

* Wed Aug 09 2017 tmb <tmb> 4.12.5-2.mga7
+ Revision: 1139281
- add current -stable queue

* Sun Aug 06 2017 tmb <tmb> 4.12.5-1.mga7
+ Revision: 1138019
- disable perf again as it's currently broken
- ahci: Add Device ID for ASMedia 1061R and 1062R
- enable perf build
- update to 4.12.5
- aufs: explicitly include linux/vmalloc.h

* Sat Aug 05 2017 tmb <tmb> 4.12.4-1.mga7
+ Revision: 1136286
- temporarliy disable perf build as texlive is not installable
- btrfs: fix early ENOSPC due to delalloc
- add 4.12.5-rc1
- disable generation of /usr/lib/.build-id links as it causes file conflicts on devel packages
- drop more obsolete conflicts
- drop old obsoletes for netbook and xen-ovops packages
- drop ancient obsoletes
- update dkms conflicts for kernel 4.12 support
- disable debug build for now, it will be reworked
- update filelists
- drop adding export of pci_ids.h, needs to be done as part of userspace-headers generation now
- move netfilter IFWLOG and PSD headers to uapi so they get exported
- fix netfilter IFWLOG build with 4.12
- export symbol __sync_filesystem for aufs
- drop rtl8723bs from 3rdparty, it's now merged in staging
- update ndiswrapper to 1.61
- fix ndiswrapper build with 4.10+ series kernels
- rediff mrproper patch
- update defconfigs
- update to aufs 4.12
- drop merged/obsolete patches
- update to 4.12.4

* Fri Jul 28 2017 tmb <tmb> 4.9.40-1.mga7
+ Revision: 1131581
- update to 4.9.40

* Mon Jul 24 2017 tmb <tmb> 4.9.39-1.mga7
+ Revision: 1130005
- drop ThinkPad X1 Carbon fan fix as it causes regressions for other hw
- add current -stable queue
- update to 4.9.39

* Mon Jul 17 2017 tmb <tmb> 4.9.38-1.mga7
+ Revision: 1123896
- update to 4.9.38

* Thu Jul 13 2017 tmb <tmb> 4.9.37-1.mga6
+ Revision: 1109699
- revert 'perf probe: Fix to probe on gcc generated functions in modules'
  introduced in upstream 4.9.36 as it breaks the build
- fix duplicated ALC285 codec references
- force new HT fixed microcode in initrd
- enable support for NFS4_1 and NFS4_2 (mga#21182)
-  Revert 'ACPI / EC: Enable event freeze mode...' to fix a regression
- ALSA: hda/realtek - New codecs support for ALC215/ALC285/ALC289
- ALSA: hda/realtek - New codec device ID for ALC1220
- platform/x86: asus-nb-wmi: Add wapf4 quirk for the X302UA
- update to 4.9.37
  * drop merged patches

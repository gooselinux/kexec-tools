Name: kexec-tools
Version: 2.0.0 
Release: 145%{?dist}
License: GPLv2
Group: Applications/System
Summary: The kexec/kdump userspace component.
Source0: http://www.kernel.org/pub/linux/kernel/people/horms/kexec-tools/%{name}-%{version}.tar.bz2
Source1: kdump.init
Source2: kdump.sysconfig
Source3: kdump.sysconfig.x86_64
Source4: kdump.sysconfig.i386
Source5: kdump.sysconfig.ppc64
Source6: kdump.sysconfig.ia64
Source7: mkdumprd
Source8: kdump.conf
Source9: http://downloads.sourceforge.net/project/makedumpfile/makedumpfile/1.3.5/makedumpfile-1.3.5.tar.gz
Source10: kexec-kdump-howto.txt
Source11: firstboot_kdump.py
Source12: mkdumprd.8
Source13: kexec-tools-po.tar.gz
Source14: 98-kexec.rules
Source15: kdump.conf.5

#######################################
# These are sources for mkdumprd2
# Which is currently in development
#######################################
Source100: dracut-files.tbz2

BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
Requires(pre): coreutils chkconfig sed zlib 
Requires: busybox >= 1.2.0, dracut, bc, kpartx, mdadm, 
BuildRequires: dash 
BuildRequires: zlib-devel zlib zlib-static elfutils-devel-static glib2-devel 
BuildRequires: pkgconfig intltool gettext 
%ifarch %{ix86} x86_64 ppc64 ia64 ppc
Obsoletes: diskdumputils netdump
%endif
ExcludeArch: s390 s390x

#START INSERT

#
# Patches 0 through 100 are meant for x86 kexec-tools enablement
#
Patch1: kexec-tools-2.0.0-i686-64G-limit.patch
Patch2: kexec-tools-2.0.0-efi-bootdata.patch

#
# Patches 101 through 200 are meant for x86_64 kexec-tools enablement
#
Patch101: kexec-tools-2.0.0-fix-page-offset.patch
Patch102: kexec-tools-2.0.0-x86_64-exclude-gart.patch
Patch103: kexec-tools-2.0.0-x86-e820-acpi-reserved-add.patch
Patch104: kexec-tools-2.0.0-x86_64-ksize.patch

#
# Patches 201 through 300 are meant for ia64 kexec-tools enablement
#

#
# Patches 301 through 400 are meant for ppc64 kexec-tools enablement
#
Patch301: kexec-tools-2.0.0-ppc64-reloc.patch
Patch302: kexec-tools-2.0.0-ppc64-omnibus.patch

#
# Patches 401 through 500 are meant for s390 kexec-tools enablement
#

#
# Patches 501 through 600 are meant for ppc kexec-tools enablement
#
Patch501: kexec-tools-2.0.0-ppc-execshield.patch

#
# Patches 601 onward are generic patches
#
Patch601: kexec-tools-2.0.0-disable-kexec-test.patch
Patch602: kexec-tools-2.0.0-makedumpfile-dynamic-build.patch
Patch603: kexec-tools-2.0.0-makedumpfile-2.6.32-utsname.patch
Patch604: kexec-tools-2.0.0-makedumpfile-boption.patch
Patch605: kexec-tools-2.0.0-makedumpfile-2.6.32-sparsemem.patch
Patch606: kexec-tools-2.0.0-makedumpfile-add-missing-opts-help.patch
Patch607: kexec-tools-2.0.0-makedumpfile-use-tmpdir.patch
Patch608: kexec-tools-2.0.0-increase-segments-max.patch
Patch609: kexec-tools-2.0.0-extend-for-large-cpu-memory.patch

%description
kexec-tools provides /sbin/kexec binary that facilitates a new
kernel to boot using the kernel's kexec feature either on a
normal or a panic reboot. This package contains the /sbin/kexec
binary and ancillary utilities that together form the userspace
component of the kernel's kexec feature.

%prep
%setup -q 

mkdir -p -m755 kcp
tar -z -x -v -f %{SOURCE9}
%patch1 -p1
%patch2 -p1

%patch101 -p1
%patch102 -p1
%patch103 -p1
%patch104 -p1

%patch301 -p1
%patch302 -p1

%patch501 -p1

%patch601 -p1
%patch602 -p1
%patch603 -p1
%patch604 -p1
%patch605 -p1
%patch606 -p1
%patch607 -p1
%patch608 -p1
%patch609 -p1

tar -z -x -v -f %{SOURCE13}

%ifarch ppc
%define archdef ARCH=ppc
%endif

%build
%ifarch ia64
# ia64 gcc seems to have a problem adding -fexception -fstack-protect and
# -param ssp-protect-size, like the %configure macro does
# while that shouldn't be a problem, and it still builds fine, it results in
# the kdump kernel hanging on kexec boot.  I don't yet know why, but since those
# options aren't critical, I'm just overrideing them here for ia64
export CFLAGS="-O2 -g -pipe -Wall -Wp,-D_FORTIFY_SOURCE=2"
%endif

%configure \
%ifarch ppc64
    --host=powerpc64-redhat-linux-gnu \
    --build=powerpc64-redhat-linux-gnu \
%endif
    --sbindir=/sbin
rm -f kexec-tools.spec.in
# setup the docs
cp %{SOURCE10} . 

make
%ifarch %{ix86} x86_64 ia64 ppc64
make -C makedumpfile-1.3.5
%endif
make -C kexec-tools-po

%install
rm -rf $RPM_BUILD_ROOT
make install DESTDIR=$RPM_BUILD_ROOT
mkdir -p -m755 $RPM_BUILD_ROOT%{_sysconfdir}/rc.d/init.d
mkdir -p -m755 $RPM_BUILD_ROOT%{_sysconfdir}/sysconfig
mkdir -p -m755 $RPM_BUILD_ROOT%{_localstatedir}/crash
mkdir -p -m755 $RPM_BUILD_ROOT%{_mandir}/man8/
mkdir -p -m755 $RPM_BUILD_ROOT%{_mandir}/man5/
mkdir -p -m755 $RPM_BUILD_ROOT%{_docdir}
mkdir -p -m755 $RPM_BUILD_ROOT%{_datadir}/kdump
mkdir -p -m755 $RPM_BUILD_ROOT%{_sysconfdir}/udev/rules.d
install -m 755 %{SOURCE1} $RPM_BUILD_ROOT%{_sysconfdir}/rc.d/init.d/kdump

SYSCONFIG=$RPM_SOURCE_DIR/kdump.sysconfig.%{_target_cpu}
[ -f $SYSCONFIG ] || SYSCONFIG=$RPM_SOURCE_DIR/kdump.sysconfig.%{_arch}
[ -f $SYSCONFIG ] || SYSCONFIG=$RPM_SOURCE_DIR/kdump.sysconfig
install -m 644 $SYSCONFIG $RPM_BUILD_ROOT%{_sysconfdir}/sysconfig/kdump

install -m 755 %{SOURCE7} $RPM_BUILD_ROOT/sbin/mkdumprd
install -m 644 %{SOURCE8} $RPM_BUILD_ROOT%{_sysconfdir}/kdump.conf
install -m 644 kexec/kexec.8 $RPM_BUILD_ROOT%{_mandir}/man8/kexec.8
install -m 755 %{SOURCE11} $RPM_BUILD_ROOT%{_datadir}/kdump/firstboot_kdump.py
install -m 644 %{SOURCE12} $RPM_BUILD_ROOT%{_mandir}/man8/mkdumprd.8
install -m 644 %{SOURCE14} $RPM_BUILD_ROOT%{_sysconfdir}/udev/rules.d/98-kexec.rules
install -m 644 %{SOURCE15} $RPM_BUILD_ROOT%{_mandir}/man5/kdump.conf.5

%ifarch %{ix86} x86_64 ia64 ppc64
install -m 755 makedumpfile-1.3.5/makedumpfile $RPM_BUILD_ROOT/sbin/makedumpfile
install -m 644 makedumpfile-1.3.5/makedumpfile.8.gz $RPM_BUILD_ROOT/%{_mandir}/man8/makedumpfile.8.gz
%endif
make -C kexec-tools-po install DESTDIR=$RPM_BUILD_ROOT
%find_lang %{name}

# untar the dracut package
mkdir -p -m755 $RPM_BUILD_ROOT/etc/kdump-adv-conf
tar -C $RPM_BUILD_ROOT/etc/kdump-adv-conf -jxvf %{SOURCE100}

#and move the custom dracut modules to the dracut directory
mkdir -p $RPM_BUILD_ROOT/usr/share/dracut/modules.d/
mv $RPM_BUILD_ROOT/etc/kdump-adv-conf/kdump_dracut_modules/* $RPM_BUILD_ROOT/usr/share/dracut/modules.d/

%clean
rm -rf $RPM_BUILD_ROOT

%post
touch /etc/kdump.conf
/sbin/chkconfig --add kdump
# This portion of the script is temporary.  Its only here
# to fix up broken boxes that require special settings 
# in /etc/sysconfig/kdump.  It will be removed when 
# These systems are fixed.

if [ -d /proc/bus/mckinley ]
then
	# This is for HP zx1 machines
	# They require machvec=dig on the kernel command line
	sed -e's/\(^KDUMP_COMMANDLINE_APPEND.*\)\("$\)/\1 machvec=dig"/' \
	/etc/sysconfig/kdump > /etc/sysconfig/kdump.new
	mv /etc/sysconfig/kdump.new /etc/sysconfig/kdump
elif [ -d /proc/sgi_sn ]
then
	# This is for SGI SN boxes
	# They require the --noio option to kexec 
	# since they don't support legacy io
	sed -e's/\(^KEXEC_ARGS.*\)\("$\)/\1 --noio"/' \
	/etc/sysconfig/kdump > /etc/sysconfig/kdump.new
	mv /etc/sysconfig/kdump.new /etc/sysconfig/kdump
fi

if [ -f /sys/hypervisor/type ] && grep -q "xen" /sys/hypervisor/type
then
	# We need to put some garbage in the kdump.conf file
	echo "Kdump_not_supported_on_Xen_domU_guest" >> /etc/kdump.conf 
fi


%postun

if [ "$1" -ge 1 ]; then
	/sbin/service kdump condrestart > /dev/null 2>&1 || :
fi

%preun
if [ "$1" = 0 ]; then
	/sbin/service kdump stop > /dev/null 2>&1 || :
	/sbin/chkconfig --del kdump
fi
exit 0

%triggerin -- firstboot
# we enable kdump everywhere except for paravirtualized xen domains; check here
if [ -f /proc/xen/capabilities ]; then
	if [ -z `grep control_d /proc/xen/capabilities` ]; then
		exit 0
	fi
fi
if [ ! -e %{_datadir}/firstboot/modules/firstboot_kdump.py ]
then
	ln -s %{_datadir}/kdump/firstboot_kdump.py %{_datadir}/firstboot/modules/firstboot_kdump.py
fi

%triggerin -- kernel-kdump
touch %{_sysconfdir}/kdump.conf


%triggerun -- firstboot
rm -f %{_datadir}/firstboot/modules/firstboot_kdump.py

%triggerpostun -- kernel kernel-xen kernel-debug kernel-PAE kernel-kdump
# List out the initrds here, strip out version nubmers
# and search for corresponding kernel installs, if a kernel
# is not found, remove the corresponding kdump initrd

#start by getting a list of all the kdump initrds
MY_ARCH=`uname -m`
if [ "$MY_ARCH" == "ia64" ]
then
	IMGDIR=/boot/efi/efi/redhat
else
	IMGDIR=/boot
fi

for i in `ls $IMGDIR/initrd*kdump.img 2>/dev/null`
do
	KDVER=`echo $i | sed -e's/^.*initrd-//' -e's/kdump.*$//'`
	if [ ! -e $IMGDIR/vmlinuz-$KDVER ]
	then
		# We have found an initrd with no corresponding kernel
		# so we should be able to remove it
		rm -f $i
	fi
done

%files -f %{name}.lang
%defattr(-,root,root,-)
/sbin/*
%{_datadir}/kdump
%config(noreplace,missingok) %verify(not md5 size mtime) %{_sysconfdir}/sysconfig/kdump
%config(noreplace,missingok) %verify(not md5 size mtime) %{_sysconfdir}/kdump.conf
%{_sysconfdir}/kdump-adv-conf/kdump_initscripts/
%{_sysconfdir}/kdump-adv-conf/kdump_sample_manifests/
%config %{_sysconfdir}/rc.d/init.d/kdump
%config %{_sysconfdir}/udev/rules.d/*
%{_datadir}/dracut/modules.d/*
%dir %{_localstatedir}/crash
%{_mandir}/man5/*
%{_mandir}/man8/*
%doc News
%doc COPYING
%doc TODO
%doc kexec-kdump-howto.txt


%changelog
* Mon Aug 30 2010 Neil Horman <nhorman@redhat.com> - 2.0.0-145
- Fixing typo, bz 627747

* Mon Aug 30 2010 Neil Horman <nhorman@redhat.com> - 2.0.0-144
- Fix install to not fail on xen domU, see bz 627747

* Wed Aug 25 2010 Amerigo Wang <amwang@redhat.com> - 2.0.0-143
- Prevent installation on xen guests. See bug 608320.

* Thu Aug 19 2010 Amerigo Wang <amwang@redhat.com> - 2.0.0-142
- Use stat -f to get fs type instead of df -T. See bug 609814.

* Thu Aug 19 2010 Amerigo Wang <amwang@redhat.com> - 2.0.0-141
- Check write permission of all possible tmp dirs. See bug 609814.

* Thu Aug 19 2010 Amerigo Wang <amwang@redhat.com> - 2.0.0-140
- Fix storage driver discovery when device label is used,
  resolve bug 621162.

* Fri Aug 13 2010 Amerigo Wang <amwang@redhat.com> - 2.0.0-139
- Don't rename ld.so.cache, use -N instead. resolve bug 609814.

* Thu Aug 12 2010 Amerigo Wang <amwang@redhat.com> - 2.0.0-138
- Fix udhcpc hang when bridge is used, resolve bug 602325.

* Wed Aug 11 2010 Amerigo Wang <amwang@redhat.com> - 2.0.0-137
- Extend for large cpu count and memory, resolves bug 607400.

* Wed Aug 11 2010 Amerigo Wang <amwang@redhat.com> - 2.0.0-136
- Increase segments max, resolves bug 615281.

* Tue Aug 10 2010 Amerigo Wang <amwang@redhat.com> - 2.0.0-135
- Update po files, resolves bug 619744.

* Mon Aug 09 2010 Amerigo Wang <amwang@redhat.com> - 2.0.0-134
- Fix a localized string in firstboot. Bug 619744.

* Wed Aug 04 2010 Neil Horman <nhorman@redhat.com> - 2.0.0-133
- Add EFI info to boot_params (bz 593109)

* Fri Jul 30 2010 Amerigo Wang <amwang@redhat.com> - 2.0.0-132
- Fix firstboot locale bug. Resolves bug 619061.

* Thu Jul 29 2010 Neil Horman <nhorman@redhat.com> - 2.0.0-131
- fix firstboot to ensure kdump svc is disabled properly (bz 594830)

* Tue Jul 27 2010 Amerigo Wang <amwang@redhat.com> - 2.0.0-130
- Show error diablog when firstboot is not configurable. Resolves bug 612745.

* Tue Jul 27 2010 Amerigo Wang <amwang@redhat.com> - 2.0.0-129
- Fix a typo in code. Resolves bug 616694.

* Mon Jul 26 2010 Neil Horman <nhorman@redhat.com> - 2.0.0-128
- Fix missing spec requires (bz 617445)

* Mon Jul 26 2010 Amerigo Wang <amwang@redhat.com> - 2.0.0-127
- Don't convert LABEL or UUID. Resolves bug 617124.

* Mon Jul 26 2010 Amerigo Wang <amwang@redhat.com> - 2.0.0-126
- Fix an awk syntax error when slashes are contained. (bug 600575)

* Mon Jul 26 2010 Amerigo Wang <amwang@redhat.com> - 2.0.0-125
- Support xfs. Resolves bug 607527.

* Fri Jul 23 2010 Amerigo Wang <amwang@redhat.com> - 2.0.0-124
- Fix the incorrect count of block devices.
  See comment #5 of bug 600575.

* Fri Jul 23 2010 Amerigo Wang <amwang@redhat.com> - 2.0.0-123
- Fix missed btrfsck. Resolves bug 616694.

* Wed Jul 21 2010 Neil Horman <nhorman@redhat.com> - 2.0.0-122
- Fixed KENREL_TEXT_SIZE value (bz 605732)

* Tue Jul 20 2010 Neil Horman <nhorman@redhat.com> - 2.0.0-121
- enhance block device detection to handle renaming better (bz 597268)

* Tue Jul 20 2010 Amerigo Wang <amwang@redhat.com> - 2.0.0-120
- Support dumping over bridge. Resolves bug 602325.

* Mon Jul 19 2010 Amerigo Wang <amwang@redhat.com> - 2.0.0-119
- Move kernel parameter checking earlier, before generating initrd.
  Resolves bug 605624.

* Thu Jul 15 2010 Neil Horman <nhorman@redhat.com> - 2.0.0-118
- Fix unmount of rootfs when selinux policy loaded (bz 612822)

* Thu Jul 15 2010 Amerigo Wang <amwang@redhat.com> - 2.0.0-117
- Ignore other core_collector's when dumping over ssh, from Neil Horman.
  Resolve bug 614303.

* Wed Jul 14 2010 Amerigo Wang <amwang@redhat.com> - 2.0.0-116
- Include makedumpfile binary by default, resolves bug 614379.

* Wed Jul 14 2010 Amerigo Wang <amwang@redhat.com> - 2.0.0-115
- Clarify core_collector in documents, resolves bug 611614.

* Wed Jul 14 2010 Amerigo Wang <amwang@redhat.com> - 2.0.0-114
- Use tcp when dumping over NFS, to avoid heavily dropped packets.
  see comment #6 in bug 613499.

* Wed Jul 14 2010 Amerigo Wang <amwang@redhat.com> - 2.0.0-113
- Use makedumpfile -c -d 31 as default, resolves bug 612183.

* Tue Jul 13 2010 Amerigo Wang <amwang@redhat.com> - 2.0.0-112
- Fix an NFS mount error, resolves bug 613499.
- Fix an ssh error on ppc64, resolves bug 602570.

* Mon Jul 12 2010 Amerigo Wang <amwang@redhat.com> - 2.0.0-111
- Disable kdump service inside xen-guest, resolves bug 608320.

* Mon Jul 12 2010 Amerigo Wang <amwang@redhat.com> - 2.0.0-110
- Fix the wrong local host name, resolves bug 612872.

* Fri Jul 09 2010 Neil Horman <nhorman@redhat.com> - 2.0.0-109
- Make i686 kexec properly specify e820 map (bz 611654)

* Fri Jul 09 2010 Amerigo Wang <amwang@redhat.com> - 2.0.0-108
- Make makedumpfile respect global TMPDIR. Resolves bug 607404.

* Fri Jul 09 2010 Amerigo Wang <amwang@redhat.com> - 2.0.0-107
- Include the patch from Cai, adding missed options to --help
  of makedumpfile. Resolves bug 606704.

* Fri Jul 09 2010 Amerigo Wang <amwang@redhat.com> - 2.0.0-106
- Fix the clock issues in RHEL6. Resolves bug 605844.

* Thu Jul 08 2010 Neil Horman <nhorman@redhat.com> - 2.0.0-105
- Fix docs to reflect bz 595956 (bz 611639)

* Wed Jul 07 2010 Amerigo Wang <amwang@redhat.com> - 2.0.0-104
- Pick a tmp directory before using it. Resolves bug 609814.

* Wed Jul 07 2010 Amerigo Wang <amwang@redhat.com> - 2.0.0-103
- msh will hang if there are no statements within while loop,
  add a no-op. Resolves bug 611667.

* Wed Jul 07 2010 Amerigo Wang <amwang@redhat.com> - 2.0.0-102
- If a symlink with the same name exists, remove it first before
  copying, so that extra_bins will be copied correctly.
  Resolves bug 611699.

* Wed Jul 07 2010 Amerigo Wang <amwang@redhat.com> - 2.0.0-101
- Copy btrfsck only when necessary. Resolves bug 611451.

* Wed Jul 07 2010 Amerigo Wang <amwang@redhat.com> - 2.0.0-100
- Display memory usage stats during kdump boot.
  Resolves bug 604808.

* Mon Jul 05 2010 Amerigo Wang <amwang@redhat.com> - 2.0.0-99
- Support btrfs, and move fs type check earlier so that
  mkdumprd will fail soon with unsupported fs type.
  Resolves bug 607515 and bug 607131.

* Mon Jul 05 2010 Amerigo Wang <amwang@redhat.com> - 2.0.0-98
- Allow using PREFIX rather than NETMASK too. Resolves bug 608582.

* Mon Jul 05 2010 Amerigo Wang <amwang@redhat.com> - 2.0.0-97
- Remove the debug statement, resolves bug 600286.

* Thu Jul 01 2010 Amerigo Wang <amwang@redhat.com> - 2.0.0-96
- Fix the patch for bug 607195. 

* Thu Jul 01 2010 Amerigo Wang <amwang@redhat.com> - 2.0.0-95
- Move modules from /lib into /lib/modules/`uname -r`, and
  regenerate modules.dep for them. Resolves bug 602033.

* Wed Jun 30 2010 Neil Horman <nhorman@redhat.com> - 2.0.0-94
- Fix addition of reserved/acpi regions (bz 600777)

* Wed Jun 30 2010 Amerigo Wang <amwang@redhat.com> - 2.0.0-93
- Fix a regression introduced by the previous patch, see
  comment #13 in bug 600607.

* Wed Jun 30 2010 Amerigo Wang <amwang@redhat.com> - 2.0.0-92
- When there are multiple net dump targets, let the last one
  overwrite the previous ones, stop showing errors in this case.
  See comment #4 in bug 600607.

* Mon Jun 28 2010 Neil Horman <nhorman@redhat.com> - 2.0.0-91
- Add warning to kdump if we exceeded resere use (bz 607195)

* Mon Jun 28 2010 Amerigo Wang <amwang@redhat.com> - 2.0.0-90
- Only include firmwares that will be used, to reduce kdump
  initrd size. Resolves bug 604151.

* Fri Jun 25 2010 Neil Horman <nhorman@redhat.com> - 2.0.0-89
- Removed remaining nash refs (bz 604787)

* Wed Jun 23 2010 Neil Horman <nhorman@redhat.com> - 2.0.0-88
- load selinux policy in initramfs (bz 597229)

* Wed Jun 23 2010 Amerigo Wang <amwang@redhat.com> - 2.0.0-87
- We don't need to escape '#' with "\#", otherwise '#' will be
  executed as a command before aliased. See comment #4 of bug 600896.

* Wed Jun 23 2010 Amerigo Wang <amwang@redhat.com> - 2.0.0-86
- When there are double quotes in LABEL= in kdump.conf, findfs
  will not be able to find the correct label, we should allow
  quotes in LABEL= in kdump.conf because a label name may contain
  spaces. See comment #4 of bug 600611.

* Tue Jun 22 2010 Neil Horman <nhorman@redhat.com> - 2.0.0-85
- disable memory cgroups in kdump (bz 605717)

* Mon Jun 21 2010 Amerigo Wang <amwang@redhat.com> - 2.0.0-84
- Fix the wrong patch for bug 600597.

* Mon Jun 21 2010 Amerigo Wang <amwang@redhat.com> - 2.0.0-83
- Add the missed patch for bug 600572.

* Fri Jun 19 2010 Neil Horman <nhorman@redhat.com> - 2.0.0-82
- prevent fsck from oeprating interactively (bz 595057)

* Tue Jun 18 2010 Amerigo Wang <amwang@redhat.com> - 2.0.0-81
- Add 4G limit to firstboot_kdump.py, resolves bug 523092.

* Tue Jun 18 2010 Amerigo Wang <amwang@redhat.com> - 2.0.0-80
- Fix the other issue in bug 603522.

* Tue Jun 16 2010 Amerigo Wang <amwang@redhat.com> - 2.0.0-79
- Fix bug 603006 and bug 603522.

* Tue Jun 15 2010 Amerigo Wang <amwang@redhat.com> - 2.0.0-78
- Forward patches from RHEL5, Resolves: bz 592312  600566
  600571  600572 600574 600575 600577 600578 600579 600581 600583
  600584  600585 600586 600588 600590 600591 600593 600594 600595
  600596 600597  600598 600599 600600 600601 600602 600604 600605
  600606 600607 600610 600611 600613 600896 602785  602905.

* Wed Jun 09 2010 Neil Horman <nhorman@redhat.com> - 2.0.0-77
- dchapmans patch to use current rootfs as default in kdump.conf (bz595956)

* Tue Jun 08 2010 Neil Horman <nhorman@redhat.com> - 2.0.0-76
- Fix blacklisting (bz 596439)

* Thu Jun 03 2010 Neil Horman <nhorman@redhat.com> - 2.0.0-75
- Fix ppc64 to work & not corrupt vmcore (bz 578067 575685)

* Wed Jun 02 2010 Neil Horman <nhorman@redhat.com> - 2.0.0-74
- Enhance initrd rebuild detection (bz 592312)

* Thu May 27 2010 Neil Horman <nhorman@redhat.com> - 2.0.0-73
- fixed raid5 module detection (bz 595809)

* Wed May 26 2010 Neil Horman <nhorman@redhat.com> - 2.0.0-72
- Fixed kdump option handling (bz 594508)
- Fixed kdump fsck pause (bz 595057)

* Mon May 24 2010 Neil Horman <nhorman@redhat.com> - 2.0.0-71
- Fixed mkdumprd to remove dup insmod (bz 591172)

* Thu May 20 2010 Neil Horman <nhorman@redhat.com> - 2.0.0-70
- Fix firstboot to find grub on EFI systems (bz 592140)
- Fix scp monitoring script (bz 593403)

* Thu May 06 2010 Neil Horman <nhorman@redhat.com> - 2.0.0-69
- Updated translations (bz 589214)

* Mon Apr 26 2010 Neil Horman <nhorman@redhat.com> - 2.0.0-68
- Remove bogus debug comment from mkdumprd. (bz 585811)

* Tue Apr  6 2010 Vitaly Mayatskikh <vmayatsk@redhat.com> - 2.0.0-67
- Handle SPARSEMEM properly (bz 574370)

* Mon Apr 05 2010 Neil Horman <nhorman@redhat.com> - 2.0.0-66
- Add blacklist feature to kdump.conf (bz 568018)

* Mon Apr 05 2010 Neil Horman <nhorman@redhat.com> - 2.0.0-65
- Fix ssh id propogation w/ selinux (bz 579477)

* Mon Apr 05 2010 Neil Horman <nhorman@redhat.com> - 2.0.0-64
- Fix major/minor numbers on /dev/rtc (bz 578411)

* Thu Apr 01 2010 Neil Horman <nhorman@redhat.com> - 2.0.0-63
- Vitaly's fix to detect need for 64 bit elf (bz 578178)

* Tue Mar 30 2010 Neil Horman <nhorman@redhat.com> - 2.0.0-62
- Update mkdumprd to deal with changes in busybox fsck (bz 577981)

* Wed Mar 24 2010 Neil Horman <nhorman@redhat.com> - 2.0.0-61
- Add ability to handle firmware hotplug events (bz 563145)

* Mon Mar 22 2010 Neil Horman <nhorman@redhat.com> - 2.0.0-60
- Add help info for -b option (bz 574305)

* Thu Mar 18 2010 Neil Horman <nhorman@redhat.com> - 2.0.0-59
- Fix critical_disks list to exclude cciss/md (bz 573624)

* Thu Mar 11 2010 Neil Horman <nhorman@redhat.com> - 2.0.0-58
- Fix spec file typo (bz 567871)

* Thu Mar 11 2010 Neil Horman <nhorman@redhat.com> - 2.0.0-57
- Enable execshield in ppc build (bz 567871)

* Wed Mar 03 2010 Neil Horman <nhorman@redhat.com> -2.0.0-56
- Added utsname support to makedumpfile for 2.6.32 (bz 556356)
- Cleaned up some syntax in the changelog

* Mon Mar 01 2010 Neil Horman <nhorman@redhat.com> -2.0.0-55
- Fixed lvm setup loop to not hang (bz 561793)

* Tue Feb 09 2010 Neil Horman <nhorman@redhat.com> - 2.0.0-54
- Fixed firstboot enable sense (bz 563062)

* Mon Feb 08 2010 Neil Horman <nhorman@redhat.com> - 2.0.0-53
- Removed rhpl code from firstboot (bz 561717)

* Fri Jan 29 2010 Neil Horman <nhorman@redhat.com> - 2.0.0-52
- Updated kexec with mr translations (bz 559099)

* Fri Jan 29 2010 Neil Horman <nhorman@redhat.com> - 2.0.0-51
- Fixed x86_64 page_offset specifictaion (bz 546549)

* Mon Jan 25 2010 Neil Horman <nhorman@redhat.com> - 2.0.0-50
- Fixed readlink issue (bz 558193)

* Wed Jan 20 2010 Neil Horman <nhorman@redhat.com> - 2.0.0-49
- Removed remaining nash calls from mkdumprd (bz 556877)

* Fri Jan 08 2010 Neil Horman <nhorman@redhat.com> - 2.0.0-48
- Added poweroff option to mkdumprd (bz 543360)

* Fri Jan 08 2010 Neil Horman <nhorman@redhat.com> - 2.0.0-47
- Fixed bad call to resolve_dm_name (bz 529393)

* Tue Dec 08 2009 Neil Horman <nhorman@redhat.com> - 2.0.0-46
- Update makedumpfile to 1.3.5 (bz 532064)

* Fri Dec 04 2009 Neil Horman <nhorman@redhat.com> - 2.0.0-45
- Fix initscript to return proper LSB return codes (bz 544161)

* Fri Nov 20 2009 Neil Horman <nhorman@redhat.com> - 2.0.0-44
- Exclude s390[x] from build (bz 538852)

* Tue Nov 17 2009 Neil Horman <nhorman@redhat.com> - 2.0.0-43
- Fixing crashkernel syntax parsing (bz 533800)

* Wed Nov 11 2009 Neil Horman <nhorman@redhat.com> - 2.0.0-42
- Cai's fix for broken regex (bz 536719)

* Fri Nov 06 2009 Neil Horman <nhorman@redhat.com> - 2.0.0-41
- Improved mkdumprd run time (bz 528737)

* Wed Nov 04 2009 Neil Horman <nhorman@redhat.com> - 2.0.0-40
- Adding -i/-x options to makedumpfile (bz 529411)

* Wed Nov 04 2009 Neil Horman <nhorman@redhat.com> - 2.0.0-39
- Fix ppc64 sysconfig file (bz 531565)

* Wed Nov 04 2009 Neil Horman <nhorman@redhat.com> - 2.0.0-38
- Update makedumpfile to v 1.3.4 (bz 529409)

* Mon Nov 02 2009 Neil Horman <nhorman@redhat.com> - 2.0.0-37
- Adding relocatable patches from bz 484465)

* Thu Oct 29 2009 Neil Horman <nhorman@redhat.com> - 2.0.0-36
- Pulling fedora fixes for dracut/kdump into RHEL6 (bz 531473)

* Mon Oct 12 2009 Neil Horman <nhorman@redhat.com> - 2.0.0-35
- Fixed kexec-kdump-howto.doc for RHEL6 (bz 525043)

* Mon Oct 12 2009 Neil Horman <nhorman@redhat.com> - 2.0.0-34
- Fix firstboot to deal with new crashkernel sytaxes (bz 525026)

* Wed Oct 07 2009 Neil Horman <nhorman@redhat.com> - 2.0.0-33
- Fix x8664 memory map changes for makedumpfile (bz 526749)
 
* Wed Sep 30 2009 Neil Horman <nhorman@redhat.com> - 2.0.0-32
- Fix infinite loop from modprobe changes (bz 524875)

* Thu Sep 24 2009 Neil Horman <nhorman@redhat.com> - 2.0.0-31
- Removed universal add of ata_piix from mkdumprd (bz 524817)

* Wed Sep 23 2009 Neil Horman <nhorman@redhat.com> - 2.0.0-30
- Fix reboot in firstboot (bz 524811)

* Tue Sep 22 2009 Neil Horman <nhorman@redhat.com> - 2.0.0-29
- Fix mkdumprd typo (bz 524820)

* Fri Sep 18 2009 Neil Horman <nhorman@redhat.com> - 2.0.0-28
- Fix typo (bz 517584)

* Fri Sep 18 2009 Neil Horman <nhorman@redhat.com> - 2.0.0-27
- Update mkdumprd to pull in all modules needed (bz 517584)

* Mon Aug 31 2009 Neil Horman <nhorman@redhat.com> - 2.0.0-26
- Update docs to reflect use of ext4 ( bz 520183)

* Mon Aug 24 2009 Neil Horman <nhorman@redhat.com> - 2.0.0-25
- Update kexec-kdump-howto.txt (bz 518604 & 518296)

* Thu Aug 13 2009 Neil Horman <nhorman@redhat.com> - 2.0.0-24
- update kdump adv conf init script & dracut module

* Wed Jul 29 2009 Neil Horman <nhorman@redhat.com> - 2.0,0-23
- Remove mkdumprd2 and start replacement with dracut

* Fri Jul 24 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.0.0-22
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Mon Jul 06 2009 Neil Horman <nhorman@redhat.com> 2.0.0-21
- Fixed build break

* Mon Jul 06 2009 Neil Horman <nhorman@redhat.com> 2.0.0-20
- Make makedumpfile a dynamic binary

* Mon Jul 06 2009 Neil Horman <nhorman@redhat.com> 2.0.0-19
- Fix build issue 

* Mon Jul 06 2009 Neil Horman <nhorman@redhat.com> 2.0.0-18
- Updated initscript to use mkdumprd2 if manifest is present
- Updated spec to require dash
- Updated sample manifest to point to correct initscript
- Updated populate_std_files helper to fix sh symlink

* Mon Jul 06 2009 Neil Horman <nhorman@redhat.com> 2.0.0-17
- Fixed mkdumprd2 tarball creation

* Wed Jun 23 2009 Neil Horman <nhorman@redhat.com> 2.0.0-16
- Fix up kdump so it works with latest firstboot

* Mon Jun 15 2009 Neil Horman <nhorman@redhat.com> 2.0.0-15
- Fixed some stat drive detect bugs by E. Biederman (bz505701)

* Wed May 20 2009 Neil Horman <nhorman@redhat.com> 2.0.0-14
- Put early copy of mkdumprd2 out in the wild (bz 466392)

* Fri May 08 2009 Neil Horman <nhorman@redhat.com> - 2.0.0-13
- Update makedumpfile to v 1.3.3 (bz 499849)

* Tue Apr 07 2009 Neil Horman <nhorman@redhat.com> - 2.0.0-12
- Simplifed rootfs mounting code in mkdumprd (bz 494416)

* Sun Apr 05 2009 Lubomir Rintel <lkundrak@v3.sk> - 2.0.0-11
- Install the correct configuration for i586

* Fri Apr 03 2009 Neil Horman <nhorman@redhat.com> - 2.0.0-10
- Fix problem with quoted CORE_COLLECTOR string (bz 493707)

* Thu Apr 02 2009 Orion Poplawski <orion@cora.nwra.com> - 2.0.0-9
- Add BR glibc-static

* Wed Feb 25 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.0.0-8
- Rebuilt for https://fedoraproject.org/wiki/Fedora_11_Mass_Rebuild

* Thu Dec 04 2008 Ignacio Vazquez-Abrams <ivazqueznet+rpm@gmail.com> - 2.0.0-7
- Rebuild for Python 2.6

* Mon Dec 01 2008 Neil Horman <nhorman@redhat.com> - 2.0.0.6
- adding makedumpfile man page updates (bz 473212)

* Mon Dec 01 2008 Ignacio Vazquez-Abrams <ivazqueznet+rpm@gmail.com> - 2.0.0-5
- Rebuild for Python 2.6

* Wed Nov 05 2008 Neil Horman <nhorman@redhat.com> - 2.0.0-3
- Correct source file to use proper lang package (bz 335191)

* Wed Oct 29 2008 Neil Horman <nhorman@redhat.com> - 2.0.0-2
- Fix mkdumprd typo (bz 469001)

* Mon Sep 15 2008 Neil Horman <nhorman@redhat.com> - 2.0.0-2
- Fix sysconfig files to not specify --args-linux on x86 (bz 461615)

* Wed Aug 27 2008 Neil Horman <nhorman@redhat.com> - 2.0.0-1
- Update kexec-tools to latest upstream version

* Wed Aug 27 2008 Neil Horman <nhorman@redhat.com> - 1.102pre-16
- Fix mkdumprd to properly use UUID/LABEL search (bz 455998)

* Tue Aug  5 2008 Tom "spot" Callaway <tcallawa@redhat.com> - 1.102pre-15
- fix license tag

* Mon Jul 28 2008 Neil Horman <nhorman@redhat.com> - 1.102pre-14
- Add video reset section to docs (bz 456572)

* Mon Jul 11 2008 Neil Horman <nhorman@redhat.com> - 1.102pre-13
- Fix mkdumprd to support dynamic busybox (bz 443878)

* Wed Jun 11 2008 Neil Horman <nhorman@redhat.com> - 1.102pre-12
- Added lvm to bin list (bz 443878)

* Thu Jun 05 2008 Neil Horman <nhorman@redhat.com> - 1.102pre-11
- Update to latest makedumpfile from upstream
- Mass import of RHEL fixes missing in rawhide

* Thu Apr 24 2008 Neil Horman <nhorman@redhat.com> - 1.102pre-10
- Fix mkdumprd to properly pull in libs for lvm/mdadm (bz 443878)

* Wed Apr 16 2008 Neil Horman <nhorman@redhat.com> - 1.102pre-9
- Fix cmdline length issue

* Tue Mar 25 2008 Neil Horman <nhorman@redhat.com> - 1.102pre-8
- Fixing ARCH definition for bz 438661

* Mon Mar 24 2008 Neil Horman <nhorman@redhat.com> - 1.102pre-7
- Adding patches for bz 438661

* Fri Feb 22 2008 Neil Horman <nhorman@redhat.com> - 1.102pre-6
- Bringing rawhide up to date with bugfixes from RHEL5
- Adding patch to prevent kexec buffer overflow on ppc (bz 428684)

* Tue Feb 19 2008 Neil Horman <nhorman@redhat.com> - 1.102pre-5
- Modifying mkdumprd to include dynamic executibles (bz 433350)

* Wed Feb 12 2008 Neil Horman <nhorman@redhat.com> - 1.102pre-4
- bumping rev number for rebuild

* Wed Jan 02 2008 Neil Horman <nhorman@redhat.com> - 1.102pre-3
- Fix ARCH placement in kdump init script (bz 427201)
- Fix BuildRequires
- Fix Makedumpfile to build with new libelf

* Mon Oct 01 2007 Neil Horman <nhorman@redhat.com> - 1.102pre-2
- Fix triggerpostun script (bz 308151)

* Mon Aug 30 2007 Neil Horman <nhorman@redhat.com> - 1.102pre-1
- Bumping kexec version to latest horms tree (bz 257201)
- Adding trigger to remove initrds when a kernel is removed

* Wed Aug 22 2007 Neil Horman <nhorman@redhat.com> - 1.101-81
- Add xen-syms patch to makedumpfile (bz 250341)

* Wed Aug 22 2007 Neil Horman <nhorman@redhat.com> - 1.101-80
- Fix ability to determine space on nfs shares (bz 252170)

* Tue Aug 21 2007 Neil Horman <nhorman@redhat.com> - 1.101-79
- Update kdump.init to always create sparse files (bz 253714)

* Fri Aug 10 2007 Neil Horman <nhorman@redhat.com> - 1.101-78
- Update init script to handle xen kernel cmdlnes (bz 250803)

* Wed Aug 01 2007 Neil Horman <nhorman@redhat.com> - 1.101-77
- Update mkdumprd to suppres notifications /rev makedumpfile (bz 250341)

* Thu Jul 19 2007 Neil Horman <nhorman@redhat.com> - 1.101-76
- Fix mkdumprd to suppress informative messages (bz 248797)

* Wed Jul 18 2007 Neil Horman <nhorman@redhat.com> - 1.101-75
- Updated fr.po translations (bz 248287)

* Mon Jul 17 2007 Neil Horman <nhorman@redhat.com> - 1.101-74
- Fix up add_buff to retry locate_hole on segment overlap (bz 247989)

* Mon Jul 09 2007 Neil Horman <nhorman@redhat.com> - 1.101-73
- Fix up language files for kexec (bz 246508)

* Thu Jul 05 2007 Neil Horman <nhorman@redhat.com> - 1.101-72
- Fixing up initscript for LSB (bz 246967)

* Tue Jun 19 2007 Neil Horman <nhorman@redhat.com> - 1.101-71
- Fixed conflict in mkdumprd in use of /mnt (bz 222911)

* Mon Jun 18 2007 Neil Horman <nhorman@redhat.com> - 1.101-70
- Fixed kdump.init to properly read cmdline (bz 244649)

* Wed Apr 11 2007 Neil Horman <nhorman@redhat.com> - 1.101-69
- Fixed up kdump.init to enforce mode 600 on authorized_keys2 (bz 235986)

* Tue Apr 10 2007 Neil Horman <nhorman@redhat.com> - 1.101-68
- Fix alignment of bootargs and device-tree structures on ppc64

* Tue Apr 10 2007 Neil Horman <nhorman@redhat.com> - 1.101-67
- Allow ppc to boot ppc64 kernels (bz 235608)

* Tue Apr 10 2007 Neil Horman <nhorman@redhat.com> - 1.101-66
- Reduce rmo_top to 0x7c000000 for PS3 (bz 235030)

* Mon Mar 26 2007 Neil Horman <nhorman@redhat.com> - 1.101-65
- Fix spec to own kexec_tools directory (bz 219035)

* Wed Mar 21 2007 Neil Horman <nhorman@redhat.com> - 1.101-64
- Add fix for ppc memory region computation (bz 233312)

* Thu Mar 15 2007 Neil Horman <nhorman@redhat.com> - 1.101-63
- Adding extra check to avoid oom kills on nfs mount failure (bz 215056)

* Tue Mar 06 2007 Neil Horman <nhorman@redhat.com> - 1.101-62
- Updating makedumpfile to version 1.1.1 (bz 2223743)

* Mon Feb 22 2007 Neil Horman <nhorman@redhat.com> - 1.101-61
- Adding multilanguage infrastructure to firstboot_kdump (bz 223175)

* Mon Feb 12 2007 Neil Horman <nhorman@redhat.com> - 1.101-60
- Fixing up file permissions on kdump.conf (bz 228137)

* Fri Feb 09 2007 Neil Horman <nhorman@redhat.com> - 1.101-59
- Adding mkdumprd man page to build

* Wed Jan 25 2007 Neil Horman <nhorman@redhat.com> - 1.101-58
- Updating kdump.init and mkdumprd with most recent RHEL5 fixes
- Fixing BuildReq to require elfutils-devel-static

* Thu Jan 04 2007 Neil Horman <nhorman@redhat.com> - 1.101-56
- Fix option parsing problem for bzImage files (bz 221272)

* Fri Dec 15 2006 Neil Horman <nhorman@redhat.com> - 1.101-55
- Wholesale update of RHEL5 revisions 55-147

* Tue Aug 29 2006 Neil Horman <nhorman@redhat.com> - 1.101-54
- integrate default elf format patch

* Tue Aug 29 2006 Neil Horman <nhorman@redhat.com> - 1.101-53
- Taking Viveks x86_64 crashdump patch (rcv. via email)

* Tue Aug 29 2006 Neil Horman <nhorman@redhat.com> - 1.101-52
- Taking ia64 tools patch for bz 181358

* Mon Aug 28 2006 Neil Horman <nhorman@redhat.com> - 1.101-51
- more doc updates
- added patch to fix build break from kernel headers change

* Thu Aug 24 2006 Neil Horman <nhorman@redhat.com> - 1.101-50
- repo patch to enable support for relocatable kernels.

* Thu Aug 24 2006 Neil Horman <nhorman@redhat.com> - 1.101-49
- rewriting kcp to properly do ssh and scp
- updating mkdumprd to use new kcp syntax

* Wed Aug 23 2006 Neil Horman <nhorman@redhat.com> - 1.101-48
- Bumping revision number 

* Tue Aug 22 2006 Jarod Wilson <jwilson@redhat.com> - 1.101-47
- ppc64 no-more-platform fix

* Mon Aug 21 2006 Jarod Wilson <jwilson@redhat.com> - 1.101-46
- ppc64 fixups:
  - actually build ppc64 binaries (bug 203407)
  - correct usage output
  - avoid segfault in command-line parsing
- install kexec man page
- use regulation Fedora BuildRoot

* Fri Aug 18 2006 Neil Horman <nhorman@redhat.com> - 1.101-45
- fixed typo in mkdumprd for bz 202983
- fixed typo in mkdumprd for bz 203053
- clarified docs in kdump.conf with examples per bz 203015

* Tue Aug 15 2006 Neil Horman <nhorman@redhat.com> - 1.101-44
- updated init script to implement status function/scrub err messages
 
* Wed Aug 09 2006 Jarod Wilson <jwilson@redhat.com> - 1.101-43
- Misc spec cleanups and macro-ifications

* Wed Aug 09 2006 Jarod Wilson <jwilson@redhat.com> - 1.101-42
- Add dir /var/crash, so default kdump setup works

* Thu Aug 03 2006 Neil Horman <nhorman@redhat.com> - 1.101-41
- fix another silly makefile error for makedumpfile 

* Thu Aug 03 2006 Neil Horman <nhorman@redhat.com> - 1.101-40
- exclude makedumpfile from build on non-x86[_64] arches 

* Thu Aug 03 2006 Neil Horman <nhorman@redhat.com> - 1.101-39
- exclude makedumpfile from build on non-x86[_64] arches 

* Thu Aug 03 2006 Neil Horman <nhorman@redhat.com> - 1.101-38
- updating makedumpfile makefile to use pkg-config on glib-2.0

* Thu Aug 03 2006 Neil Horman <nhorman@redhat.com> - 1.101-37
- updating makedumpfile makefile to use pkg-config

* Thu Aug 03 2006 Neil Horman <nhorman@redhat.com> - 1.101-36
- Removing unneeded deps after Makefile fixup for makedumpfile

* Thu Aug 03 2006 Neil Horman <nhorman@redhat.com> - 1.101-35
- fixing up FC6/RHEL5 BuildRequires line to build in brew

* Wed Aug 02 2006 Neil Horman <nhorman@redhat.com> - 1.101-34
- enabling makedumpfile in build

* Wed Aug 02 2006 Neil Horman <nhorman@redhat.com> - 1.101-33
- added makedumpfile source to package

* Mon Jul 31 2006 Neil Horman <nhorman@redhat.com> - 1.101-32
- added et-dyn patch to allow loading of relocatable kernels

* Thu Jul 27 2006 Neil Horman <nhorman@redhat.com> - 1.101-30
- fixing up missing patch to kdump.init

* Wed Jul 19 2006 Neil Horman <nhorman@redhat.com> - 1.101-30
- add kexec frontend (bz 197695)

* Wed Jul 12 2006 Jesse Keating <jkeating@redhat.com> - 1.101-29
- rebuild

* Wed Jul 07 2006 Neil Horman <nhorman@redhat.com> 1.101-27
- Buildrequire zlib-devel

* Thu Jun 22 2006 Neil Horman <nhorman@redhat.com> -1.101-19
- Bumping rev number

* Thu Jun 22 2006 Neil Horman <nhorman@redhat.com> -1.101-17
- Add patch to allow ppc64 to ignore args-linux option

* Wed Mar 08 2006 Bill Nottingham <notting@redhat.com> - 1.101-16
- fix scriptlet - call chkconfig --add, change the default in the
  script itself (#183633)

* Wed Mar 08 2006 Thomas Graf <tgraf@redhat.com> - 1.101-15
- Don't add kdump service by default, let the user manually add it to
  avoid everyone seeing a warning.

* Tue Mar 07 2006 Thomas Graf <tgraf@redhat.com> - 1.101-14
- Fix kdump.init to call kexec from its new location

* Mon Mar  6 2006 Jeremy Katz <katzj@redhat.com> - 1.101-13
- proper requires for scriptlets

* Mon Mar 06 2006 Thomas Graf <tgraf@redhat.com> - 1.101-12
- Move kexec and kdump binaries to /sbin

* Thu Mar 02 2006 Thomas Graf <tgraf@redhat.com> - 1.101-11
- Fix argument order when stopping kexec

* Mon Feb 27 2006 Thomas Graf <tgraf@redhat.com> - 1.101-10
- kdump7.patch
   o Remove elf32 core headers support for x86_64
   o Fix x86 prepare elf core header routine
   o Fix ppc64 kexec -p failure for gcc 4.10
   o Fix few warnings for gcc 4.10
   o Add the missing --initrd option for ppc64
   o Fix ppc64 persistent root device bug
- Remove --elf32-core-headers from default configuration, users
  may re-add it via KEXEC_ARGS.
- Remove obsolete KEXEC_HEADERS
* Wed Feb 22 2006 Thomas Graf <tgraf@redhat.com> - 1.101-9
- Remove wrong quotes around --command-line in kdump.init

* Fri Feb 17 2006 Jeff Moyer <jmoyer@redhat.com> - 1.101-8
- Fix the service stop case.  It was previously unloading the wrong kernel.
- Implement the "restart" function.
- Add the "irqpoll" option as a default kdump kernel commandline parameter.
- Create a default kernel command line in the sysconfig file upon rpm install.

* Tue Feb 07 2006 Jesse Keating <jkeating@redhat.com> - 1.101-7.1.1
- rebuilt for new gcc4.1 snapshot and glibc changes

* Thu Feb 02 2006 Thomas Graf <tgraf@redhat.com> - 1.101-7.1
- Add patch to enable the kdump binary for x86_64
* Wed Feb 01 2006 Thomas Graf <tgraf@redhat.com>
- New kdump patch to support s390 arch + various fixes
- Include kdump in x86_64 builds
* Mon Jan 30 2006 Thomas Graf <tgraf@redhat.com>
- New kdump patch to support x86_64 userspace

* Fri Dec 16 2005 Jesse Keating <jkeating@redhat.com>
- rebuilt for new gcj

* Wed Nov 16 2005 Thomas Graf <tgraf@redhat.com> - 1.101-5
- Report missing kdump kernel image as warning
 
* Thu Nov  3 2005 Jeff Moyer <jmoyer@redhat.com> - 1.101-4
- Build for x86_64 as well.  Kdump support doesn't work there, but users
  should be able to use kexec.

* Fri Sep 23 2005 Jeff Moyer <jmoyer@redhat.com> - 1.101-3
- Add a kdump sysconfig file and init script
- Spec file additions for pre/post install/uninstall

* Thu Aug 25 2005 Jeff Moyer <jmoyer@redhat.com>
- Initial prototype for RH/FC5

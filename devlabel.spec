Summary:	Consistent/persistent storage device access through symlinking
Name:		devlabel
Version:	0.48.01
Release:	1
License:	GPL
Group:		System Environment/Base
Group:		Applications/System
Source0:	http://linux.dell.com/devlabel/permalink/%{name}-%version.tar.gz
# Source0-md5:	1a4032b942d8b47544da1957374a9786
Requires:	sed grep awk textutils fileutils diffutils coreutils mktemp
Requires:	initscripts > 6.97-1
Requires:	util-linux
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
This package contains the devlabel implementation. It allows for
consistent mounting of devices. This is accomplished through tagging a
unique identifier to each device/symlink combination and confirming
that the identifier still matches the device name before it allows the
symlink mapping to proceed.

%prep

%setup -q

%build
gcc $RPM_OPT_FLAGS -o scsi_unique_id scsi_unique_id.c
gcc $RPM_OPT_FLAGS -o partition_uuid -luuid partition_uuid.c

%pre
[ -d /var/lib/devlabel ] && rm -rf /var/lib/devlabel >/dev/null 2>&1
if [ -e /etc/sysconfig/devlabel ]; then
	devlabel_version=`devlabel -v 2>/dev/null`
	old_format=""
	version_major=`echo $devlabel_version | awk {'print $2'} | cut -d '.' -f 1-1`
	version_minor=`echo $devlabel_version | awk {'print $2'} | cut -d '.' -f 2-2`
	[ -z "$version_minor" ] && old_format="true"
	[ -z "$old_format" ] && [ "$version_major" -eq 0 ] && [ "$version_minor" -lt 37 ] && old_format="true"
        if [ -n "$old_format" ]; then
                /sbin/devlabel restart >/dev/null 2>&1 || :
        fi
fi

%triggerpostun -- devlabel <= 0.38.07-1
if [ -e /etc/sysconfig/devlabel ]; then
	/sbin/devlabel reverseremap --force >/dev/null 2>&1 || :
fi

%install
rm -rf $RPM_BUILD_ROOT
if [ "$RPM_BUILD_ROOT" != "/" ]; then
	rm -rf $RPM_BUILD_ROOT
fi
install -d $RPM_BUILD_ROOT/{sbin,usr/bin,usr/share/man/man8,etc/sysconfig,etc/sysconfig/devlabel.d}
install -m 755 devlabel $RPM_BUILD_ROOT/sbin/devlabel
install -m 755 scsi_unique_id $RPM_BUILD_ROOT%{_bindir}
install -m 755 partition_uuid $RPM_BUILD_ROOT%{_bindir}
install devlabel.8.gz $RPM_BUILD_ROOT%{_mandir}/man8
install sysconfig.devlabel $RPM_BUILD_ROOT/etc/sysconfig/devlabel
install ignore_list $RPM_BUILD_ROOT/etc/sysconfig/devlabel.d
install ignore_list $RPM_BUILD_ROOT/etc/sysconfig/devlabel.d/proc_partitions

%clean
if [ "$RPM_BUILD_ROOT" != "/" ]; then
	rm -rf $RPM_BUILD_ROOT
fi

%files
%defattr(644,root,root,755)
%attr(755,root,root) %{_sbindir}/devlabel
%attr(755,root,root) %{_bindir}/scsi_unique_id
%attr(755,root,root) %{_bindir}/partition_uuid
/etc/sysconfig/devlabel.d
%config(noreplace) /etc/sysconfig/devlabel
%{_mandir}/man8/devlabel.8*
%doc AUTHORS COPYING

Summary:	Consistent/persistent storage device access through symlinking
Summary(pl):	Spójny/sta³y dostêp do urz±dzeñ z danymi poprzez symlinki
Name:		devlabel
Version:	0.48.01
Release:	1
License:	GPL
Group:		Applications/System
Source0:	http://linux.dell.com/devlabel/permalink/%{name}-%{version}.tar.gz
# Source0-md5:	1a4032b942d8b47544da1957374a9786
BuildRequires:	libuuid-devel
Requires:	awk
Requires:	coreutils
Requires:	diffutils
Requires:	grep
Requires:	mktemp
Requires:	rc-scripts
Requires:	sed
Requires:	util-linux
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define		_sbindir	/sbin

%description
This package contains the devlabel implementation. It allows for
consistent mounting of devices. This is accomplished through tagging a
unique identifier to each device/symlink combination and confirming
that the identifier still matches the device name before it allows the
symlink mapping to proceed.

%description -l pl
Ten pakiet zawiera implementacjê devlabel. Umo¿liwia spójne montowanie
urz±dzeñ. Osi±ga to poprzez oznaczanie unikalnymi identyfikatorami
ka¿dej kombinacji urz±dzenie/symlink i potwierdzanie, ¿e dany
identyfikator nadal pasuje do nazwy urz±dzenia przed umo¿liwieniem
odwzorowania dowi±zania symbolicznego.

%prep
%setup -q

%build
%{__cc} %{rpmcflags} -o scsi_unique_id scsi_unique_id.c
%{__cc} %{rpmcflags} -o partition_uuid -luuid partition_uuid.c

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
install -d $RPM_BUILD_ROOT{%{_sbindir},%{_bindir},%{_mandir}/man8,/etc/sysconfig/devlabel.d}

install devlabel $RPM_BUILD_ROOT%{_sbindir}/devlabel
install scsi_unique_id $RPM_BUILD_ROOT%{_bindir}
install partition_uuid $RPM_BUILD_ROOT%{_bindir}
gzip -dc devlabel.8.gz > $RPM_BUILD_ROOT%{_mandir}/man8/devlabel.8
install sysconfig.devlabel $RPM_BUILD_ROOT/etc/sysconfig/devlabel
install ignore_list $RPM_BUILD_ROOT/etc/sysconfig/devlabel.d
install ignore_list $RPM_BUILD_ROOT/etc/sysconfig/devlabel.d/proc_partitions

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(644,root,root,755)
%doc AUTHORS
%attr(755,root,root) %{_sbindir}/devlabel
%attr(755,root,root) %{_bindir}/scsi_unique_id
%attr(755,root,root) %{_bindir}/partition_uuid
/etc/sysconfig/devlabel.d
%config(noreplace) %verify(not md5 mtime size) /etc/sysconfig/devlabel
%{_mandir}/man8/devlabel.8*

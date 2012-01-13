%define		modname	memcached
%define		status		stable
Summary:	interface to memcached via libmemcached library
Summary(pl.UTF-8):	interfejs do memcached z użyciem biblioteki libmemcached
Name:		php-pecl-%{modname}
Version:	1.0.2
Release:	9
License:	PHP
Group:		Development/Languages/PHP
Source0:	http://pecl.php.net/get/%{modname}-%{version}.tgz
# Source0-md5:	b91f815ad59086d0c3564cce022b5c4f
URL:		http://pecl.php.net/package/memcached/
BuildRequires:	libmemcached-devel
BuildRequires:	php-devel >= 3:5.0.0
BuildRequires:	rpmbuild(macros) >= 1.344
BuildRequires:	zlib-devel
%{?requires_php_extension}
Requires:	php-common >= 4:5.0.4
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
This extension uses libmemcached library to provide API for
communicating with memcached servers.

In PECL status of this extension is: %{status}.

%description -l pl.UTF-8
Rozszerzenie to wykorzystuje bibliotekę memcached w celu udostępnienia
API do komunikacji z serwerami memcached.

To rozszerzenie ma w PECL status: %{status}.

%prep
%setup -q -c
mv %{modname}-%{version}/* .

%build
phpize
%configure
%{__make}

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT%{php_sysconfdir}/conf.d

%{__make} install \
	INSTALL_ROOT=$RPM_BUILD_ROOT \
	EXTENSION_DIR=%{php_extensiondir}
cat <<'EOF' > $RPM_BUILD_ROOT%{php_sysconfdir}/conf.d/%{modname}.ini
; Enable %{modname} extension module
extension=%{modname}.so
EOF

%clean
rm -rf $RPM_BUILD_ROOT

%post
%php_webserver_restart

%postun
if [ "$1" = 0 ]; then
	%php_webserver_restart
fi

%files
%defattr(644,root,root,755)
%doc CREDITS
%config(noreplace) %verify(not md5 mtime size) %{php_sysconfdir}/conf.d/%{modname}.ini
%attr(755,root,root) %{php_extensiondir}/%{modname}.so

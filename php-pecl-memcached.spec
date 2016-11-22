%define		php_name	php%{?php_suffix}
%define		modname	memcached
Summary:	Interface to memcached via libmemcached library
Summary(pl.UTF-8):	Interfejs do memcached z użyciem biblioteki libmemcached
Name:		%{php_name}-pecl-%{modname}
Version:	3.0.0
Release:	0.1
License:	PHP 3.01
Group:		Development/Languages/PHP
Source0:	https://github.com/php-memcached-dev/php-memcached/archive/php7/%{modname}-%{version}.tar.gz
# Source0-md5:	df81b124ac101bd21922deb0ef2ad9b9
URL:		http://pecl.php.net/package/memcached/
BuildRequires:	%{php_name}-devel >= 4:5.2.0
BuildRequires:	cyrus-sasl-devel
BuildRequires:	libmemcached-devel >= 1.0
BuildRequires:	rpmbuild(macros) >= 1.650
BuildRequires:	zlib-devel
%{?requires_php_extension}
Suggests:	%{php_name}-pecl-igbinary
Provides:	php(%{modname}) = %{version}
Obsoletes:	php-pecl-memcached < 2.2.0-1
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
This extension uses libmemcached library to provide API for
communicating with memcached servers.

%description -l pl.UTF-8
Rozszerzenie to wykorzystuje bibliotekę memcached w celu udostępnienia
API do komunikacji z serwerami memcached.

%prep
%setup -qc
mv php-memcached-*/{.??*,*} .

%build
phpize
%configure \
	--enable-memcached-json
%{__make}

%install
rm -rf $RPM_BUILD_ROOT
%{__make} install \
	INSTALL_ROOT=$RPM_BUILD_ROOT \
	EXTENSION_DIR=%{php_extensiondir}

install -d $RPM_BUILD_ROOT%{php_sysconfdir}/conf.d
cat <<'EOF' > $RPM_BUILD_ROOT%{php_sysconfdir}/conf.d/%{modname}.ini
; Enable %{modname} extension module
extension=%{modname}.so

EOF
cat %{modname}.ini >> $RPM_BUILD_ROOT%{php_sysconfdir}/conf.d/%{modname}.ini

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

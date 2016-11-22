#
# Conditional build:
%bcond_without	igbinary	# memcached igbinary serializer support
%bcond_without	json		# memcached json serializer support
%bcond_without	msgpack		# memcached msgpack serializer support
%bcond_without	sasl		# memcached sasl support
%bcond_without	session		# memcached session handler support
%bcond_without	tests		# build without tests

%define		php_name	php%{?php_suffix}
%define		modname	memcached
Summary:	Interface to memcached via libmemcached library
Summary(pl.UTF-8):	Interfejs do memcached z użyciem biblioteki libmemcached
Name:		%{php_name}-pecl-%{modname}
# for PHP < 7 support see 2.2.x branch
Version:	3.0.0
Release:	1
License:	PHP 3.01
Group:		Development/Languages/PHP
Source0:	https://github.com/php-memcached-dev/php-memcached/archive/php7/%{modname}-%{version}.tar.gz
# Source0-md5:	df81b124ac101bd21922deb0ef2ad9b9
URL:		http://pecl.php.net/package/memcached/
BuildRequires:	%{php_name}-devel >= 4:7.0.0
%{?with_igbinary:BuildRequires:	%{php_name}-pecl-igbinary-devel}
%{?with_msgpack:BuildRequires:	%{php_name}-pecl-msgpack-devel}
%{?with_sasl:BuildRequires:	cyrus-sasl-devel}
BuildRequires:	fastlz-devel
BuildRequires:	libmemcached-devel >= 1.0.18
BuildRequires:	pkgconfig
BuildRequires:	re2c
BuildRequires:	rpmbuild(macros) >= 1.650
BuildRequires:	zlib-devel
%if %{with tests}
BuildRequires:	%{php_name}-cli
BuildRequires:	%{php_name}-pcre
%{?with_igbinary:BuildRequires:	%{php_name}-pecl-igbinary}
%{?with_msgpack:BuildRequires:	%{php_name}-pecl-msgpack}
%{?with_session:BuildRequires:	%{php_name}-session}
BuildRequires:	%{php_name}-spl
%endif
%{?requires_php_extension}
Suggests:	%{php_name}-pecl-igbinary
Suggests:	%{php_name}-pecl-msgpack
Suggests:	%{php_name}-session
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

rm fastlz/fastlz.c

# redirect tests fail (the actual tests they redirect work)
rm tests/experimental/serializer_igbinary.phpt
rm tests/experimental/serializer_json.phpt

%build
phpize
%configure \
	%{__enable_disable igbinary memcached-igbinary} \
	%{__enable_disable json memcached-json} \
	%{__enable_disable msgpack memcached-msgpack} \
	%{__enable_disable sasl memcached-sasl} \
	%{__enable_disable session memcached-session} \
	--with-system-fastlz
%{__make}

%if %{with tests}
# simple module load test
%{__php} -n -q \
	-d extension_dir=modules \
	-d extension=%{php_extensiondir}/pcre.so \
	-d extension=%{php_extensiondir}/spl.so \
%if %{with session}
	-d extension=%{php_extensiondir}/session.so \
%endif
%if %{with igbinary}
	-d extension=%{php_extensiondir}/igbinary.so \
%endif
%if %{with msgpack}
	-d extension=%{php_extensiondir}/msgpack.so \
%endif
	-d extension=%{modname}.so \
	-m > modules.log
grep %{modname} modules.log

cat <<'EOF' > run-tests.sh
#!/bin/sh
export NO_INTERACTION=1 REPORT_EXIT_STATUS=1 MALLOC_CHECK_=2
exec %{__make} test \
	PHP_EXECUTABLE=%{__php} \
	PHP_TEST_SHARED_SYSTEM_EXTENSIONS="spl%{?with_session: session}%{?with_igbinary: igbinary}%{?with_msgpack: msgpack}" \
	RUN_TESTS_SETTINGS="-q $*"
EOF
chmod +x run-tests.sh

./run-tests.sh
%endif

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

%define realname apc (Alternative PHP Cache)
%define modname apc
%define dirname %{modname}
%define soname %{modname}.so
%define inifile 99_%{modname}.ini

%define _requires_exceptions pear(

Summary:	The %{realname} module for PHP
Name:		php-%{modname}
Version:	3.0.18
Release:	%mkrel 2
Group:		Development/PHP
License:	PHP License
URL:		http://pecl.php.net/package/APC
Source0:	http://pecl.php.net/get/APC-%{version}.tgz
Source1:	apc.ini
BuildRequires:  php-devel >= 3:5.2.0
Conflicts:	php-afterburner php-mmcache php-eaccelerator
Epoch:		1
Buildroot:	%{_tmppath}/%{name}-%{version}-%{release}-buildroot

%description
APC was conceived of to provide a way of boosting the performance of PHP on
heavily loaded sites by providing a way for scripts to be cached in a compiled
state, so that the overhead of parsing and compiling can be almost completely
eliminated. There are commercial products which provide this functionality, but
they are neither open-source nor free. Our goal was to level the playing field
by providing an implementation that allows greater flexibility and is
universally accessible. 

We also wanted the cache to provide visibility into it's own workings and those
of PHP, so time was invested in providing internal diagnostic tools which allow
for cache diagnostics and maintenance. 

Thus arrived APC. Since we were committed to developing a product which can
easily grow with new version of PHP, we implemented it as a zend extension,
allowing it to either be compiled into PHP or added post facto as a drop in
module. As with PHP, it is available completely free for commercial
and non-commercial use, under the same terms as PHP itself.

APC has been tested under PHP 4.0.3, 4.0.3pl1 and 4.0.4. It currently compiles
under Linux and FreeBSD. Patches for ports to other OSs/ PHP versions are
welcome.

NOTE!: %{name} has to be loaded last, very important!

This package comes with four different flavours of APC (use only one of them):

 o apc-mmap.so - mmap (fcntl) based locks (default)
 o apc-sem.so - IPC semamphore based locks
 o apc-spinlocks.so - Hardware-dependent implementation of spinlocks
 o apc-pthread.so - NPTL pthread mutex based locks

%package	admin
Summary:	Web admin GUI for %{realname}
Group:		Development/PHP
Requires(pre): rpm-helper
Requires(postun): rpm-helper
Requires:	apache-mod_php
Requires:	%{name}

%description	admin
This package contains a Web admin GUI for %{realname}.

To access the web GUI please open up your favourite web browser and point to:

http://localhost/%{name}/

%prep

%setup -q -n APC-%{version}
[ "../package*.xml" != "/" ] && mv ../package*.xml .

cp %{SOURCE1} %{inifile}

%build
%serverbuild

phpize

mkdir -p build-apc-mmap
pushd build-apc-mmap
ln -s ../configure .
%configure2_5x \
    --enable-%{modname}=shared,%{_prefix} \
    --enable-apc-filehits \
    --disable-apc-pthreadmutex \
    --disable-apc-sem \
    --disable-apc-futex \
    --disable-apc-spinlocks \
    --enable-apc-mmap

%make
popd

mkdir -p build-apc-sem
pushd build-apc-sem
ln -s ../configure .
%configure2_5x \
    --enable-%{modname}=shared,%{_prefix} \
    --enable-apc-filehits \
    --disable-apc-pthreadmutex \
    --disable-apc-mmap \
    --disable-apc-futex \
    --disable-apc-spinlocks \
    --enable-apc-sem

%make
popd

mkdir -p build-apc-spinlocks
pushd build-apc-spinlocks
ln -s ../configure .
%configure2_5x \
    --enable-%{modname}=shared,%{_prefix} \
    --enable-apc-filehits \
    --disable-apc-pthreadmutex \
    --disable-apc-mmap \
    --disable-apc-futex \
    --disable-apc-sem \
    --disable-apc-mmap \
    --enable-apc-spinlocks

%make
popd

mkdir -p build-apc-pthread
pushd build-apc-pthread
ln -s ../configure .
%configure2_5x \
    --enable-%{modname}=shared,%{_prefix} \
    --enable-apc-filehits \
    --disable-apc-mmap \
    --disable-apc-futex \
    --disable-apc-spinlocks \
    --disable-apc-sem \
    --disable-apc-mmap

%make
popd

%install
[ "%{buildroot}" != "/" ] && rm -rf %{buildroot}

install -d %{buildroot}%{_libdir}/php/extensions
install -d %{buildroot}%{_sysconfdir}/php.d
install -d %{buildroot}/var/www/%{name}
install -d %{buildroot}%{_sysconfdir}/httpd/conf/webapps.d

install -m0644 %{inifile} %{buildroot}%{_sysconfdir}/php.d/%{inifile}

install -m0755 build-apc-mmap/modules/apc.so %{buildroot}%{_libdir}/php/extensions/apc-mmap.so
install -m0755 build-apc-sem/modules/apc.so %{buildroot}%{_libdir}/php/extensions/apc-sem.so
install -m0755 build-apc-spinlocks/modules/apc.so %{buildroot}%{_libdir}/php/extensions/apc-spinlocks.so
install -m0755 build-apc-pthread/modules/apc.so %{buildroot}%{_libdir}/php/extensions/apc-pthread.so

cat > %{name}.conf << EOF
Alias /%{name} /var/www/%{name}

<Directory "/var/www/%{name}">
    Order deny,allow
    Deny from all
    Allow from 127.0.0.1
    ErrorDocument 403 "Access denied per %{_sysconfdir}/httpd/conf/webapps.d/%{name}.conf"
</Directory>
EOF

install -m0644 %{name}.conf %{buildroot}%{_sysconfdir}/httpd/conf/webapps.d/
install -m0644 apc.php %{buildroot}/var/www/%{name}/index.php

%post
if [ -f /var/lock/subsys/httpd ]; then
    %{_initrddir}/httpd restart >/dev/null || :
fi

%postun
if [ "$1" = "0" ]; then
    if [ -f /var/lock/subsys/httpd ]; then
	%{_initrddir}/httpd restart >/dev/null || :
    fi
fi

%post admin
%_post_webapp

%postun admin
%_postun_webapp

%clean
[ "%{buildroot}" != "/" ] && rm -rf %{buildroot}

%files
%defattr(-,root,root)
%doc tests CHANGELOG INSTALL LICENSE NOTICE TECHNOTES.txt TODO package*.xml
%attr(0644,root,root) %config(noreplace) %{_sysconfdir}/php.d/%{inifile}
%attr(0755,root,root) %{_libdir}/php/extensions/apc-mmap.so
%attr(0755,root,root) %{_libdir}/php/extensions/apc-sem.so
%attr(0755,root,root) %{_libdir}/php/extensions/apc-spinlocks.so
%attr(0755,root,root) %{_libdir}/php/extensions/apc-pthread.so

%files admin
%defattr(-,root,root)
%attr(0644,root,root) %config(noreplace) %{_sysconfdir}/httpd/conf/webapps.d/%{name}.conf
%dir /var/www/%{name}
/var/www/%{name}/index.php

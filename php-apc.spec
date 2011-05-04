%define _disable_ld_no_undefined 1

%define realname apc (Alternative PHP Cache)
%define modname apc
%define dirname %{modname}
%define soname %{modname}.so
%define inifile 99_%{modname}.ini

%define _requires_exceptions pear(

Summary:	The %{realname} module for PHP
Name:		php-%{modname}
Version:	3.1.7
Release:	%mkrel 3
Group:		Development/PHP
License:	PHP License
URL:		http://pecl.php.net/package/APC
Source0:	http://pecl.php.net/get/APC-%{version}.tgz
Source1:	apc.ini
Patch0:		APC-3.1.3p1-default_lock_dir.diff
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

NOTE!: %{name} has to be loaded last, very important!

This package comes with four different flavours of APC (use only one of them):

 o apc-mmap.so - mmap (fcntl) based locks (default)
 o apc-sem.so - IPC semamphore based locks
 o apc-spinlocks.so - Hardware-dependent implementation of spinlocks
 o apc-pthread.so - NPTL pthread mutex based locks

%package	admin
Summary:	Web admin GUI for %{realname}
Group:		Development/PHP
%if %mdkversion < 201010
Requires(post):   rpm-helper
Requires(postun):   rpm-helper
%endif
Requires:	apache-mod_php
Requires:	%{name}

%description	admin
This package contains a Web admin GUI for %{realname}.

To access the web GUI please open up your favourite web browser and point to:

http://localhost/%{name}/

%prep

%setup -q -n APC-%{version}
[ "../package*.xml" != "/" ] && mv ../package*.xml .

%patch0 -p0

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
    --disable-apc-pthreadrwlocks \
    --disable-apc-sem \
    --disable-apc-spinlocks \
    --enable-apc-mmap \
    --enable-apc-memprotect

%make
popd

mkdir -p build-apc-sem
pushd build-apc-sem
ln -s ../configure .
%configure2_5x \
    --enable-%{modname}=shared,%{_prefix} \
    --enable-apc-filehits \
    --disable-apc-pthreadmutex \
    --disable-apc-pthreadrwlocks \
    --disable-apc-mmap \
    --disable-apc-spinlocks \
    --enable-apc-sem \
    --enable-apc-memprotect

%make
popd

mkdir -p build-apc-spinlocks
pushd build-apc-spinlocks
ln -s ../configure .
%configure2_5x \
    --enable-%{modname}=shared,%{_prefix} \
    --enable-apc-filehits \
    --disable-apc-pthreadmutex \
    --disable-apc-pthreadrwlocks \
    --disable-apc-sem \
    --disable-apc-mmap \
    --disable-apc-memprotect \
    --enable-apc-spinlocks

%make
popd

mkdir -p build-apc-pthread
pushd build-apc-pthread
ln -s ../configure .
%configure2_5x \
    --enable-%{modname}=shared,%{_prefix} \
    --enable-apc-filehits \
    --enable-apc-pthreadrwlocks \
    --disable-apc-spinlocks \
    --disable-apc-mmap \
    --disable-apc-sem \
    --disable-apc-memprotect
%make
popd

%install
rm -rf %{buildroot}

install -d %{buildroot}%{_libdir}/php/extensions
install -d %{buildroot}%{_sysconfdir}/php.d
install -d %{buildroot}/var/www/%{name}
install -d %{buildroot}/var/lib/php-apc

install -m0644 %{inifile} %{buildroot}%{_sysconfdir}/php.d/%{inifile}

install -m0755 build-apc-mmap/modules/apc.so %{buildroot}%{_libdir}/php/extensions/apc-mmap.so
install -m0755 build-apc-sem/modules/apc.so %{buildroot}%{_libdir}/php/extensions/apc-sem.so
install -m0755 build-apc-spinlocks/modules/apc.so %{buildroot}%{_libdir}/php/extensions/apc-spinlocks.so
install -m0755 build-apc-pthread/modules/apc.so %{buildroot}%{_libdir}/php/extensions/apc-pthread.so

install -d -m 755 %{buildroot}%{webappconfdir}
cat > %{buildroot}%{webappconfdir}/%{name}.conf << EOF
Alias /%{name} /var/www/%{name}

<Directory "/var/www/%{name}">
    Order deny,allow
    Deny from all
    Allow from 127.0.0.1
    ErrorDocument 403 "Access denied per %{webappconfdir}/%{name}.conf"
</Directory>
EOF

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
%if %mdkversion < 201010
%_post_webapp
%endif

%postun admin
%if %mdkversion < 201010
%_postun_webapp
%endif

%clean
rm -rf %{buildroot}

%files
%defattr(-,root,root)
%doc tests CHANGELOG INSTALL LICENSE NOTICE TECHNOTES.txt TODO package*.xml
%attr(0644,root,root) %config(noreplace) %{_sysconfdir}/php.d/%{inifile}
%attr(0755,root,root) %{_libdir}/php/extensions/apc-mmap.so
%attr(0755,root,root) %{_libdir}/php/extensions/apc-sem.so
%attr(0755,root,root) %{_libdir}/php/extensions/apc-spinlocks.so
%attr(0755,root,root) %{_libdir}/php/extensions/apc-pthread.so
%attr(0755,apache,apache) /var/lib/php-apc

%files admin
%defattr(-,root,root)
%config(noreplace) %{webappconfdir}/%{name}.conf
%dir /var/www/%{name}
/var/www/%{name}/index.php

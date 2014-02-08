%define _disable_ld_no_undefined 1

%define realname apc (Alternative PHP Cache)
%define modname apc
%define dirname %{modname}
%define soname %{modname}.so
%define inifile 99_%{modname}.ini

Summary:	The %{realname} module for PHP
Name:		php-%{modname}
Version:	3.1.12
Release:	3
Group:		Development/PHP
License:	PHP License
URL:		http://pecl.php.net/package/APC
Source0:	http://pecl.php.net/get/APC-%{version}.tgz
Source1:	apc.ini
Patch0:		APC-3.1.3p1-default_lock_dir.diff
Patch1:		APC-3.1.9-svn_fixes.diff
BuildRequires:  php-devel >= 3:5.2.0
Conflicts:	php-afterburner php-mmcache php-eaccelerator
Epoch:		1

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
 o apc-mmap+mutex.so - mmap (fcntl) and pthread mutex based locks

%package	admin
Summary:	Web admin GUI for %{realname}
Group:		Development/PHP
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

mkdir -p build-apc-mmap+mutex
pushd build-apc-mmap+mutex
ln -s ../configure .
%configure2_5x \
    --enable-%{modname}=shared,%{_prefix} \
    --enable-apc-filehits \
    --enable-apc-mmap \
    --enable-apc-pthreadmutex
%make
popd

%install
install -d %{buildroot}%{_libdir}/php/extensions
install -d %{buildroot}%{_sysconfdir}/php.d
install -d %{buildroot}/var/www/%{name}
install -d %{buildroot}/var/lib/php-apc

install -m0644 %{inifile} %{buildroot}%{_sysconfdir}/php.d/%{inifile}

install -m0755 build-apc-mmap/modules/apc.so %{buildroot}%{_libdir}/php/extensions/apc-mmap.so
install -m0755 build-apc-sem/modules/apc.so %{buildroot}%{_libdir}/php/extensions/apc-sem.so
install -m0755 build-apc-spinlocks/modules/apc.so %{buildroot}%{_libdir}/php/extensions/apc-spinlocks.so
install -m0755 build-apc-pthread/modules/apc.so %{buildroot}%{_libdir}/php/extensions/apc-pthread.so
install -m0755 build-apc-mmap+mutex/modules/apc.so %{buildroot}%{_libdir}/php/extensions/apc-mmap+mutex.so

install -d -m 755 %{buildroot}%{_webappconfdir}
cat > %{buildroot}%{_webappconfdir}/%{name}.conf << EOF
Alias /%{name} /var/www/%{name}

<Directory "/var/www/%{name}">
    Require host 127.0.0.1
    ErrorDocument 403 "Access denied per %{_webappconfdir}/%{name}.conf"
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

%files
%doc tests CHANGELOG INSTALL LICENSE NOTICE TECHNOTES.txt TODO package*.xml
%attr(0644,root,root) %config(noreplace) %{_sysconfdir}/php.d/%{inifile}
%attr(0755,root,root) %{_libdir}/php/extensions/apc-mmap.so
%attr(0755,root,root) %{_libdir}/php/extensions/apc-sem.so
%attr(0755,root,root) %{_libdir}/php/extensions/apc-spinlocks.so
%attr(0755,root,root) %{_libdir}/php/extensions/apc-pthread.so
%attr(0755,root,root) %{_libdir}/php/extensions/apc-mmap+mutex.so
%attr(0755,apache,apache) /var/lib/php-apc

%files admin
%config(noreplace) %{_webappconfdir}/%{name}.conf
%dir /var/www/%{name}
/var/www/%{name}/index.php


%changelog
* Mon Aug 27 2012 Danila Leontiev <danila.leontiev@rosalab.ru> 1:3.1.12-1
- Updated

* Sun Jan 15 2012 Oden Eriksson <oeriksson@mandriva.com> 1:3.1.9-3.2
- rebuilt for php-5.3.9
- fix #64711 (Add an APC flavor providing mmap shared memory and pthread mutex locking)

* Fri Nov 04 2011 Oden Eriksson <oeriksson@mandriva.com> 1:3.1.9-3.1
- P1: fix #64683 (APC will crash with default config)

* Wed Aug 24 2011 Oden Eriksson <oeriksson@mandriva.com> 1:3.1.9-3mdv2011.0
+ Revision: 696367
- rebuilt for php-5.3.8

* Fri Aug 19 2011 Oden Eriksson <oeriksson@mandriva.com> 1:3.1.9-2
+ Revision: 695311
- rebuilt for php-5.3.7

* Sun May 15 2011 Oden Eriksson <oeriksson@mandriva.com> 1:3.1.9-1
+ Revision: 674765
- 3.1.9

* Wed May 04 2011 Oden Eriksson <oeriksson@mandriva.com> 1:3.1.7-3
+ Revision: 667477
- mass rebuild

* Sat Mar 19 2011 Oden Eriksson <oeriksson@mandriva.com> 1:3.1.7-2
+ Revision: 646551
- rebuilt for php-5.3.6

* Tue Jan 25 2011 Oden Eriksson <oeriksson@mandriva.com> 1:3.1.7-1
+ Revision: 632496
- 3.1.7

* Sat Jan 08 2011 Oden Eriksson <oeriksson@mandriva.com> 1:3.1.6-3mdv2011.0
+ Revision: 629736
- rebuilt for php-5.3.5

* Mon Jan 03 2011 Oden Eriksson <oeriksson@mandriva.com> 1:3.1.6-2mdv2011.0
+ Revision: 628042
- ensure it's built without automake1.7

* Wed Dec 01 2010 Oden Eriksson <oeriksson@mandriva.com> 1:3.1.6-1mdv2011.0
+ Revision: 604427
- 3.1.6

* Tue Nov 23 2010 Oden Eriksson <oeriksson@mandriva.com> 1:3.1.5-3mdv2011.0
+ Revision: 600174
- rebuild

* Tue Nov 16 2010 Colin Guthrie <cguthrie@mandriva.org> 1:3.1.5-2mdv2011.0
+ Revision: 598093
- Update .ini file syntax as per upstream change

* Wed Nov 03 2010 Oden Eriksson <oeriksson@mandriva.com> 1:3.1.5-1mdv2011.0
+ Revision: 592813
- 3.1.5

* Sun Oct 24 2010 Oden Eriksson <oeriksson@mandriva.com> 1:3.1.4-2mdv2011.0
+ Revision: 588711
- rebuild

* Thu Sep 16 2010 Oden Eriksson <oeriksson@mandriva.com> 1:3.1.4-1mdv2011.0
+ Revision: 578865
- 3.1.4

* Fri Mar 05 2010 Oden Eriksson <oeriksson@mandriva.com> 1:3.1.3p1-8mdv2010.1
+ Revision: 514513
- rebuilt for php-5.3.2

* Mon Feb 22 2010 Oden Eriksson <oeriksson@mandriva.com> 1:3.1.3p1-7mdv2010.1
+ Revision: 509464
- rebuild
- rebuild

* Mon Feb 08 2010 Guillaume Rousse <guillomovitch@mandriva.org> 1:3.1.3p1-5mdv2010.1
+ Revision: 502375
- rely on filetrigger for reloading apache configuration begining with 2010.1, rpm-helper macros otherwise

* Sat Jan 02 2010 Oden Eriksson <oeriksson@mandriva.com> 1:3.1.3p1-4mdv2010.1
+ Revision: 485254
- rebuilt for php-5.3.2RC1

* Sat Nov 21 2009 Oden Eriksson <oeriksson@mandriva.com> 1:3.1.3p1-3mdv2010.1
+ Revision: 468081
- rebuilt against php-5.3.1

* Wed Sep 30 2009 Oden Eriksson <oeriksson@mandriva.com> 1:3.1.3p1-2mdv2010.0
+ Revision: 451211
- rebuild

* Fri Aug 14 2009 Oden Eriksson <oeriksson@mandriva.com> 1:3.1.3p1-1mdv2010.0
+ Revision: 416309
- 3.1.3p1
- update the apc.ini file
- set default lock directory

* Sun Jul 19 2009 Raphaël Gertz <rapsys@mandriva.org> 1:3.1.2-8mdv2010.0
+ Revision: 397261
- Rebuild

* Sun Jul 05 2009 Colin Guthrie <cguthrie@mandriva.org> 1:3.1.2-7mdv2010.0
+ Revision: 392645
- Rebuild for new PHP

* Mon Jun 01 2009 Colin Guthrie <cguthrie@mandriva.org> 1:3.1.2-6mdv2010.0
+ Revision: 381839
- Rebuild for new PHP

* Wed May 13 2009 Oden Eriksson <oeriksson@mandriva.com> 1:3.1.2-5mdv2010.0
+ Revision: 375353
- rebuilt against php-5.3.0RC2

* Sun Mar 01 2009 Oden Eriksson <oeriksson@mandriva.com> 1:3.1.2-4mdv2009.1
+ Revision: 346391
- rebuilt for php-5.2.9

* Tue Feb 17 2009 Oden Eriksson <oeriksson@mandriva.com> 1:3.1.2-3mdv2009.1
+ Revision: 341500
- rebuilt against php-5.2.9RC2

* Wed Dec 31 2008 Oden Eriksson <oeriksson@mandriva.com> 1:3.1.2-2mdv2009.1
+ Revision: 321724
- rebuild

* Wed Dec 31 2008 Oden Eriksson <oeriksson@mandriva.com> 1:3.1.2-1mdv2009.1
+ Revision: 321640
- 3.1.2
- update the apc.ini file a bit

* Fri Dec 05 2008 Oden Eriksson <oeriksson@mandriva.com> 1:3.0.19-4mdv2009.1
+ Revision: 310211
- rebuilt against php-5.2.7

* Tue Dec 02 2008 Oden Eriksson <oeriksson@mandriva.com> 1:3.0.19-3mdv2009.1
+ Revision: 309246
- rebuild

* Sat Jul 19 2008 Oden Eriksson <oeriksson@mandriva.com> 1:3.0.19-2mdv2009.0
+ Revision: 238637
- use _disable_ld_no_undefined due to lack of time
- rebuild

* Thu May 15 2008 Oden Eriksson <oeriksson@mandriva.com> 1:3.0.19-1mdv2009.0
+ Revision: 207595
- 3.0.19

* Fri May 02 2008 Oden Eriksson <oeriksson@mandriva.com> 1:3.0.18-2mdv2009.0
+ Revision: 200171
- rebuilt for php-5.2.6

* Sat Mar 29 2008 Oden Eriksson <oeriksson@mandriva.com> 1:3.0.18-1mdv2008.1
+ Revision: 191096
- 3.0.18

* Wed Mar 26 2008 Oden Eriksson <oeriksson@mandriva.com> 1:3.0.17-1mdv2008.1
+ Revision: 190233
- 3.0.17 (fixes CVE-2008-1488)

* Mon Feb 04 2008 Oden Eriksson <oeriksson@mandriva.com> 1:3.0.16-2mdv2008.1
+ Revision: 162102
- rebuild

* Thu Dec 27 2007 Oden Eriksson <oeriksson@mandriva.com> 1:3.0.16-1mdv2008.1
+ Revision: 138463
- 3.0.16
- provide two more flavours of the extension and mention it in the description

  + Thierry Vignaud <tv@mandriva.org>
    - kill re-definition of %%buildroot on Pixel's request

* Sun Nov 11 2007 Oden Eriksson <oeriksson@mandriva.com> 1:3.0.15-2mdv2008.1
+ Revision: 107602
- restart apache if needed

* Fri Oct 19 2007 Oden Eriksson <oeriksson@mandriva.com> 1:3.0.15-1mdv2008.1
+ Revision: 100285
- 3.0.15

* Sat Sep 01 2007 Oden Eriksson <oeriksson@mandriva.com> 1:3.0.14-5mdv2008.0
+ Revision: 77526
- rebuilt against php-5.2.4

* Thu Jun 14 2007 Oden Eriksson <oeriksson@mandriva.com> 1:3.0.14-4mdv2008.0
+ Revision: 39481
- use distro conditional -fstack-protector

* Fri Jun 01 2007 Oden Eriksson <oeriksson@mandriva.com> 1:3.0.14-3mdv2008.0
+ Revision: 33796
- rebuilt against new upstream version (5.2.3)

* Thu May 03 2007 Oden Eriksson <oeriksson@mandriva.com> 1:3.0.14-2mdv2008.0
+ Revision: 21317
- rebuilt against new upstream version (5.2.2)

* Wed Apr 18 2007 Oden Eriksson <oeriksson@mandriva.com> 1:3.0.14-1mdv2008.0
+ Revision: 14499
- 3.0.14


* Wed Feb 28 2007 Oden Eriksson <oeriksson@mandriva.com> 3.0.13-1mdv2007.0
+ Revision: 127336
- 3.0.13

* Thu Feb 08 2007 Oden Eriksson <oeriksson@mandriva.com> 1:3.0.12p2-5mdv2007.1
+ Revision: 117543
- rebuilt against new upstream version (5.2.1)

* Tue Jan 16 2007 David Walluck <walluck@mandriva.org> 1:3.0.12p2-4mdv2007.1
+ Revision: 109612
- rebuild to fix missing x86-64 package

* Wed Nov 08 2006 Oden Eriksson <oeriksson@mandriva.com> 1:3.0.12p2-3mdv2007.0
+ Revision: 78123
- fix deps
- bunzip the ini file
- fix a better error 404 message

* Wed Nov 08 2006 Oden Eriksson <oeriksson@mandriva.com> 1:3.0.12p2-2mdv2007.0
+ Revision: 78053
-rebuilt for php-5.2.0
- Import php-apc

* Mon Sep 18 2006 Oden Eriksson <oeriksson@mandriva.com> 1:3.0.12p2-1
- 3.0.12p2

* Mon Aug 28 2006 Oden Eriksson <oeriksson@mandriva.com> 1:3.0.11-2
- rebuilt for php-5.1.6

* Tue Aug 22 2006 Oden Eriksson <oeriksson@mandriva.com> 1:3.0.11-1mdv2007.0
- 3.0.11
- updated apc.ini (S1)

* Thu Jul 27 2006 Oden Eriksson <oeriksson@mandriva.com> 1:3.0.10-5mdk
- rebuild

* Tue May 16 2006 Oden Eriksson <oeriksson@mandriva.com> 3.0.10-4mdk
- fix #22482

* Sat May 06 2006 Oden Eriksson <oeriksson@mandriva.com> 3.0.10-3mdk
- rebuilt for php-5.1.3

* Wed Mar 22 2006 Oden Eriksson <oeriksson@mandriva.com> 1:3.0.10-2mdk
- rebuild

* Sun Mar 12 2006 Oden Eriksson <oeriksson@mandriva.com> 1:3.0.10-1mdk
- 3.0.10

* Sun Mar 05 2006 Oden Eriksson <oeriksson@mandriva.com> 1:3.0.9-1mdk
- 3.0.9
- fix apache 2.2.0 config syntax
- use the webapps policy

* Sun Jan 15 2006 Oden Eriksson <oeriksson@mandriva.com> 1:3.0.8-3mdk
- rebuilt against php-5.1.2

* Wed Nov 30 2005 Oden Eriksson <oeriksson@mandriva.com> 1:3.0.8-2mdk
- rebuilt against php-5.1.1

* Sat Nov 26 2005 Oden Eriksson <oeriksson@mandriva.com> 1:3.0.8-1mdk
- rebuilt against php-5.1.0
- fix versioning

* Sun Oct 02 2005 Oden Eriksson <oeriksson@mandriva.com> 5.1.0_3.0.8-1mdk
- rebuilt against php-5.1.0RC1

* Fri Sep 30 2005 Oden Eriksson <oeriksson@mandriva.com> 5.0.4_3.0.8-1mdk
- works for php5 too!

* Fri Sep 30 2005 Oden Eriksson <oeriksson@mandriva.com> 4.4.0_3.0.8-1mdk
- 3.0.8
- provide both mmap and ipc based lock enabled builds
- added the web admin sub package

* Tue Jul 12 2005 Oden Eriksson <oeriksson@mandriva.com> 4.4.0-1mdk
- rebuilt for php-4.4.0 final

* Wed Jul 06 2005 Oden Eriksson <oeriksson@mandriva.com> 4.4.0-0.RC2.1mdk
- rebuilt for php-4.4.0RC2

* Wed Jun 15 2005 Oden Eriksson <oeriksson@mandriva.com> 4.4.0_2.0.4-0.RC1.1mdk
- rebuilt for php-4.4.0RC1

* Fri Jun 03 2005 Oden Eriksson <oeriksson@mandriva.com> 4.3.11_2.0.4-1mdk
- renamed to php4-*

* Sun Apr 17 2005 Oden Eriksson <oeriksson@mandriva.com> 4.3.11_2.0.4-1mdk
- 4.3.11

* Mon Mar 21 2005 Oden Eriksson <oeriksson@mandrakesoft.com> 4.3.10_2.0.4-4mdk
- use the %%mkrel macro

* Sat Feb 12 2005 Oden Eriksson <oeriksson@mandrakesoft.com> 4.3.10_2.0.4-3mdk
- rebuilt against a non hardened-php aware php lib

* Sat Jan 15 2005 Oden Eriksson <oeriksson@mandrakesoft.com> 4.3.10_2.0.4-2mdk
- rebuild due to hardened-php-0.2.6
- cleanups

* Thu Dec 16 2004 Oden Eriksson <oeriksson@mandrakesoft.com> 4.3.10_2.0.4-1mdk
- rebuild for php 4.3.10

* Wed Dec 08 2004 Oden Eriksson <oeriksson@mandrakesoft.com> 4.3.9_2.0.4-2mdk
- make it work

* Sat Oct 02 2004 Oden Eriksson <oeriksson@mandrakesoft.com> 4.3.9_2.0.4-1mdk
- rebuild for php 4.3.9

* Mon Aug 02 2004 Oden Eriksson <oeriksson@mandrakesoft.com> 4.3.8_2.0.4-2mdk
- make it work again...

* Sun Jul 18 2004 Oden Eriksson <oeriksson@mandrakesoft.com> 4.3.8_2.0.4-1mdk
- 2.0.4

* Thu Jul 15 2004 Oden Eriksson <oeriksson@mandrakesoft.com> 4.3.8_2.0.3-1mdk
- rebuilt for php-4.3.8

* Tue Jul 13 2004 Oden Eriksson <oeriksson@mandrakesoft.com> 4.3.7_2.0.3-2mdk
- remove redundant provides

* Tue Jun 15 2004 Oden Eriksson <oeriksson@mandrakesoft.com> 4.3.7_2.0.3-1mdk
- rebuilt for php-4.3.7

* Mon May 24 2004 Oden Eriksson <oeriksson@mandrakesoft.com> 4.3.6_2.0.3-2mdk
- use the %%configure2_5x macro
- move scandir to /etc/php4.d

* Thu May 06 2004 Oden Eriksson <oeriksson@mandrakesoft.com> 4.3.6_2.0.3-1mdk
- 2.0.3
- fix url
- built for php 4.3.6


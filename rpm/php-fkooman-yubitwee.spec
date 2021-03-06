%global commit0 ef37f95778b7ce31a9874f80b1f376b1f4e42749
%global shortcommit0 %(c=%{commit0}; echo ${c:0:7})

Name:           php-fkooman-yubitwee
Version:        1.1.0
Release:        1%{?dist}
Summary:        YubiKey OTP Validator library

License:        MIT
URL:            https://github.com/fkooman/php-yubitwee
Source0:        https://github.com/fkooman/php-yubitwee/archive/%{commit0}.tar.gz#/%{name}-%{shortcommit0}.tar.gz

BuildArch:      noarch

BuildRequires:  php(language) >= 5.4.0
BuildRequires:  php-curl
BuildRequires:  php-date
BuildRequires:  php-hash
BuildRequires:  php-pcre
BuildRequires:  php-spl
BuildRequires:  php-composer(fedora/autoloader)
BuildRequires:  php-composer(paragonie/constant_time_encoding)
BuildRequires:  php-composer(paragonie/random_compat)
BuildRequires:  php-composer(symfony/polyfill-php56)
BuildRequires:  %{_bindir}/phpunit

Requires:       php(language) >= 5.4.0
Requires:       php-curl
Requires:       php-date
Requires:       php-hash
Requires:       php-pcre
Requires:       php-spl
Requires:       php-composer(fedora/autoloader)
Requires:       php-composer(paragonie/constant_time_encoding)
Requires:       php-composer(paragonie/random_compat)
Requires:       php-composer(symfony/polyfill-php56)

Provides:       php-composer(fkooman/yubitwee) = %{version}

%description
A very simple, secure YubiKey OTP Validator with pluggable HTTP client.

%prep
%autosetup -n php-yubitwee-%{commit0}

%build
cat <<'AUTOLOAD' | tee src/autoload.php
<?php
require_once '%{_datadir}/php/Fedora/Autoloader/autoload.php';

\Fedora\Autoloader\Autoload::addPsr4('fkooman\\YubiTwee\\', __DIR__);
\Fedora\Autoloader\Dependencies::required(array(
    '%{_datadir}/php/ParagonIE/ConstantTime/autoload.php',
    '%{_datadir}/php/random_compat/autoload.php',
    '%{_datadir}/php/Symfony/Polyfill/autoload.php',
));
AUTOLOAD

%install
mkdir -p %{buildroot}%{_datadir}/php/fkooman/YubiTwee
cp -pr src/* %{buildroot}%{_datadir}/php/fkooman/YubiTwee

%check
cat <<'AUTOLOAD' | tee tests/autoload.php
<?php
require_once '%{_datadir}/php/Fedora/Autoloader/autoload.php';

\Fedora\Autoloader\Autoload::addPsr4('fkooman\\YubiTwee\\Tests\\', __DIR__);
\Fedora\Autoloader\Dependencies::required(array(
    '%{buildroot}/%{_datadir}/php/fkooman/YubiTwee/autoload.php',
));
AUTOLOAD

%{_bindir}/phpunit tests --verbose --bootstrap=tests/autoload.php

%files
%license LICENSE
%doc composer.json CHANGES.md README.md
%dir %{_datadir}/php/fkooman
%{_datadir}/php/fkooman/YubiTwee

%changelog
* Tue Sep 12 2017 François Kooman <fkooman@tuxed.net> - 1.1.0-1
- update to 1.1.0

* Wed Aug 30 2017 François Kooman <fkooman@tuxed.net> - 1.0.1-2
- rework spec, to align it with practices document

* Thu Jun 01 2017 François Kooman <fkooman@tuxed.net> - 1.0.1-1
- update to 1.0.1
- license changed to MIT

* Tue Apr 11 2017 François Kooman <fkooman@tuxed.net> - 1.0.0-1
- initial package

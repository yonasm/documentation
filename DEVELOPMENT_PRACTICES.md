**NOTE**: this is a work in progress!

# Introduction

This post will describe my development practices for 
[PHP](https://secure.php.net/) software development running in production on 
[CentOS](https://centos.org/) and 
[Red Hat Enterprise Linux](https://www.redhat.com/en/technologies/linux-platforms/enterprise-linux).
 
It will be long, contain a lot of details and hopefully this will be useful for
your own projects! It assumes you already have a basic knowledge of PHP 
programming and some experience deploying software. The document will show you 
"DevOps" on steroids!

These practices slowly "evolved" while developing [eduVPN](https://eduvpn.org/) 
and [Let's Connect](https://letsconnect-vpn.org/). These are projects sharing
the same code base that can be used to run your own managed VPN service. The 
code can be found [here](https://github.com/eduVPN/).

This document will describe the tools I use, why I use them, why I do not use
some popular tools and how I achieve (hopefully) high quality code without 
relying (exclusively) on proprietary tools and cloud services.

This document will walk through development, packaging and finally deployment 
by creating a web application, 
[yubicheck](https://github.com/fkooman/yubicheck), that uses an existing 
library, [yubitwee](https://github.com/fkooman/php-yubitwee).

# Principles

As I need to write code that runs on CentOS, I need to target PHP 5.4. This 
EOLed version of PHP is maintained by Red Hat, which means I will rely on 
them to fix (critical) security problems in PHP and the rest of the OS. I'm 
doing all development and testing initially on the latest release of 
[Fedora](https://getfedora.org/), which typically includes the latest version 
of PHP, at this time of writing PHP 7.1. This means, my code will run on all 
PHP versions >= 5.4.

Unfortunately targeting PHP 5.4 rules out a number of useful libraries, for 
example the OAuth 2.0 
[client](https://github.com/thephpleague/oauth2-client) and 
[server](http://oauth2.thephpleague.com/) libraries of 
[The League of Extraordinary Packages](http://thephpleague.com/). However, this 
opens the door for writing minimal libraries that only do what is needed and
nothing more.

Talking about using dependencies, these are my general rules I try to follow as
much as possible. I have these rules to make sure they actually work, reduce 
the amount of code, guarantee high quality and do not require me to constantly
chase after them. This all for the benefit of security and easy maintainability 
of the code:

- Supports PHP 5.4;
- Do not use frameworks (see below);
- Minimize the number of dependencies (and dependencies of dependencies) as 
  much as possible;
- Only use high quality, stable, small libraries that follow 
  [Semantic Versioning](http://semver.org/);
- Prefer dependencies that are already properly packaged in 
  CentOS/[EPEL](https://fedoraproject.org/wiki/EPEL);

So whenever I write something and think I can use a dependency for certain 
functionality, I check the distribution's package repository to see if there is 
already a package available that provides that functionality. If not, I search 
for the most popular, simplest library that takes care of my needs, usually 
through the amazing [Packagist](https://packagist.org/). If it does 
not exist, all available options are too complicated/bloated, or targets PHP 
versions > 5.4, I write my own and try to write a minimally functional library 
with extensive testing included. 

If the software is of use outside the VPN project I release it as free 
software and submit a package request once the software stabilizes to have it 
included in the distribution(s). Luckily, CentOS/EPEL contains already a large 
number of high quality dependencies!

Some dependencies that made the cut, i.e. followed the principles mentioned 
above:

- [Twig](https://twig.symfony.com/), a PHP template engine;
- [Symfony PHP polyfills](https://github.com/symfony/polyfill), to make 
  some functionality from PHP versions > 5.4 available in 5.4;
- [Constant-Time Character Encoding in PHP Projects](https://github.com/paragonie/constant_time_encoding); 
- [QR codes](https://github.com/Bacon/BaconQrCode);
- [OTP](https://github.com/ChristianRiesen/otp); 

Some already widely used and available dependencies that I found through e.g. 
Packagist, that did not follow my principles, for which I wrote my own 
versions:

- [Secure Cookie and Session library for PHP](https://github.com/fkooman/php-secookie);
- [YubiKey Validator](https://github.com/fkooman/php-yubitwee);
- [Very simple OAuth 2.0 client](https://github.com/fkooman/php-oauth2-client);
- [Very simple OAuth 2.0 server](https://github.com/fkooman/php-oauth2-server);

The rationale for creating each of those libraries is described in the their 
accompanying `README.md` file. Those are also published on Packagist, more on 
that later.

## PHP 5.4

The biggest problem with using PHP 5.4 as a minimum is the lack of support of 
some of the libraries I wanted to use. It turns out it is not that hard to 
develop PHP code that is compatible with all versions of PHP. The only really 
annoying thing is the lack of static typing in older PHP versions. However, 
this can be mitigated somewhat by using Psalm and provide annotations as much 
as possible, that will also ease later conversion to statically typed code.

## Frameworks

**XXX: this section is still pretty weak, could be better!**

There are a number of reasons not to use (popular) frameworks in the software. 
Most, like [Laravel](https://laravel.com/) or 
[Slim](https://www.slimframework.com/) target newer versions of PHP which rules 
them out. Technically, older versions of [Symfony](https://symfony.com/) would 
be an option, it is even packaged for Fedora and EPEL. To sum up the main 
reasons for not using a framework: 

* Does not support PHP 5.4;
* Solves way too much;
* We do not want to implement REST at all;
* No interest in having extensive database migration/update support and object
  mapping;
* No interest in chasing framework updates;

See the excellent [PHP - The Wrong Way](http://www.phpthewrongway.com/) for 
more critique on frameworks and common dogmatic approaches to software 
development.

# Tools

As a general rule here, I only use free software tools. Furthermore, I try to 
limit the dependency on external services as much as possible, and if they are
used, have a migration path to move away from them if needed. This mostly 
applies to [GitHub](https://github.com/) and 
[Packagist](https://packagist.org/).

This also applies to services like [Travis CI](https://travis-ci.com/) and 
[Scrutinizer](https://scrutinizer-ci.com/). I started out using them when the 
project started, but it turned out there are now a number of high quality 
(locally running) tools available that accomplish the same, or even perform 
better.

I do not use an IDE, I really tried 
[PhpStorm](https://www.jetbrains.com/phpstorm/), but it is too heavy for my 
taste and does a lot of stuff I do not want it to do. Recently I quickly 
evaluated [Visual Studio Code](https://code.visualstudio.com/) which doesn't 
seem that bad, but I quickly forgot it and turned back to my favorite editor. 
I use [gedit](https://wiki.gnome.org/Apps/Gedit) which is a simple editor for 
[GNOME](https://www.gnome.org/). The following is a list of tools I regularly 
use for development:

- [Git](https://git-scm.com/), for version control;
- [composer](https://getcomposer.org/), for PHP dependency management in the 
  development stage;
- [PHPStan](https://github.com/phpstan/phpstan), for static code analysis;
- [PHP-CS-Fixer](https://github.com/FriendsOfPhp/PHP-CS-Fixer), for source code 
  formatting;
- [Psalm](https://getpsalm.org/), static analysis tool for PHP;
- [Phan](https://github.com/phan/phan), another static analysis tool for PHP, 
  I initially used it, but switched to Psalm and PHPStan;
- [PHPMD](https://phpmd.org/) to view the mess I made;
- [PHP_CompatInfo](http://php5.laurent-laville.org/compatinfo/), to determine 
  PHP version requirements and PHP extensions used by the code;
- [PHPUnit](https://phpunit.de/), to run unit tests;

## Travis CI

I feel I need to explain why I'm not using Travis CI (anymore). The main reason
is that running tests of the code on Travis CI does not actually test in the 
environment the code will be actually deployed on. I'm deploying on CentOS 7, 
not on Ubuntu with a custom compiled PHP binary without for example a PECL 
extensions I use a lot, 
[libsodium](https://www.gitbook.com/book/jedisct1/libsodium/details) that 
requires too much fiddling to get working. Of course you could work around this 
by using [Docker](https://www.docker.com/) inside Travis CI to actually test on
CentOS 7, but why bother? I can easily run those same tests using 
[Mock](https://github.com/rpm-software-management/mock/wiki), but more on that 
later!

## Tool Installation

To install all the tools mentioned above and set up your Fedora development 
machine:

    $ sudo dnf -y install fedora-packager git composer php-cs-fixer \
        php-phpmd-PHP-PMD php-bartlett-PHP-CompatInfo php-phpunit-PHPUnit \
        php-pecl-xdebug yum-utils nosync

As PHPStan and Psalm do not (yet) have a package for Fedora, we install it 
"globally" for the current user:

    $ composer global require phpstan/phpstan
    $ composer global require vimeo/psalm

Add the following to `$HOME/.bash_profile` just before the `export PATH`: 

    PATH=$PATH:$HOME/.config/composer/vendor/bin

Log out and in again to activate the new path. Now you should be able to use
`phpstan` and `psalm` directly from the terminal.

# Development

As mentioned above, we'll create two projects: 

* [yubitwee](https://github.com/fkooman/php-yubitwee) - YubiKey OTP Validator 
  library
* [yubicheck](https://github.com/fkooman/yubicheck) - YubiKey OTP Validator 
  web application

We choose these two because they show the two different kinds of packages we 
will create. They differ somewhat, so it makes sense to address both types.

## Library

The library was already developed before writing this document, so we will not
get into details here, but focus on the packaging here. You can see the link
above to see the source code and the folder structure.

## Web Application

    $ mkdir -p $HOME/Projects/yubicheck
    $ cd ${HOME}/Projects/yubicheck
    $ mkdir src web tests
    $ composer init

Regarding dependencies, you need to use `fkooman/yubitwee` as a `require` 
dependency, and `phpunit/phpunit` as a `require-dev`:

    $ composer init
    Package name (<vendor>/<name>) [fkooman/yubicheck]: 
    Description []: A simple YubiKey OTP checker for the Web
    Author [François Kooman <fkooman@tuxed.net>, n to skip]: 
    Minimum Stability []: 
    Package Type (e.g. library, project, metapackage, composer-plugin) []: project
    License []: MIT

    Define your dependencies.

    Would you like to define your dependencies (require) interactively [yes]? 
    Search for a package: fkooman/yubitwee
    Enter the version constraint to require (or leave blank to use the latest version): ^1
    Search for a package: 
    Would you like to define your dev dependencies (require-dev) interactively [yes]? 
    Search for a package: phpunit/phpunit
    Enter the version constraint to require (or leave blank to use the latest version): ^5
    Search for a package: 

    {
        "name": "fkooman/yubicheck",
        "description": "A simple YubiKey OTP checker for the Web",
        "type": "project",
        "require": {
            "fkooman/yubitwee": "^1"
        },
        "require-dev": {
            "phpunit/phpunit": "^5"
        },
        "license": "MIT",
        "authors": [
            {
                "name": "François Kooman",
                "email": "fkooman@tuxed.net"
            }
        ]
    }

    Do you confirm generation [yes]? 

It is also required to add information about the classes we are about to create 
for the autoloader to work:

    "autoload": {
        "psr-4": {
            "fkooman\\YubiCheck\\": "src/",
            "fkooman\\YubiCheck\\Tests\\": "tests/"
        }
    },

Now you can run `composer update` to fetch all dependencies and generate the 
autoloader.

If you want to use a library that is not available through Packagist, e.g. you
wrote your own library that is not (yet) ready for public consumption or you 
don't want to give any stability guarantees for, you can directly point to your 
own (private) repository. This is described in the Composer 
[documentation](https://getcomposer.org/doc/05-repositories.md#vcs) on the 
subject.

It should be noted explicitly that we only use Composer for _development_ 
purposes. It will not be used or required for deploying the software to a 
server later.

## Tests

Running tests can be done with PHPUnit:

    $ phpunit tests --verbose --color

To also perform code coverage analysis, this will create a HTML report in the
`coverage/` folder:

    $ phpunit tests --verbose --color --whitelist src --coverage-html coverage

You can also create a (default) configuration file:

    $ phpunit --generate-configuration

## Code Analysis

PHPMD:

    $ phpmd "src,web,tests" text "cleancode,codesize,controversial,design,naming,unusedcode"

PHPStan:

    $ phpstan analyse -l 7 src web tests

Psalm:

    $ psalm --init
    $ psalm

A useful option is `--update-docblocks` to automatically at return types to 
"docblocks", especially useful for adding `@return void` if your IDE or editor
does not take care of that.

## Source Formatting

In order to "fix" the source code according to source code standards, e.g. 
[PSR-1](http://www.php-fig.org/psr/psr-1/), 
[PSR-2](http://www.php-fig.org/psr/psr-2/) and 
[Symfony](https://symfony.com/doc/current/contributing/code/standards.html) 
standards I use PHP-CS-Fixer.

Run the source formatting:

    $ php-cs-fixer fix . --rules=@Symfony

There are many more rules to fix things, the above is good start though. I 
use a configuration file for the projects that fixes a bit more, this is 
places as `.php_cs.dist` in the project root:

    <?php

    return PhpCsFixer\Config::create()
        ->setRiskyAllowed(true)
        ->setRules(
            [
                '@Symfony' => true,
                '@Symfony:risky' => true,
                'ordered_imports' => true,
                'ordered_class_elements' => true,
                'array_syntax' => ['syntax' => 'short'],
                'phpdoc_order' => true,
                'phpdoc_types_order' => true,
                'phpdoc_no_empty_return' => false,
                'phpdoc_add_missing_param_annotation' => true,
                'strict_comparison' => true,
                'strict_param' => true,
                'php_unit_strict' => true,
            ]
        )
        ->setFinder(PhpCsFixer\Finder::create()->in(__DIR__));

Many more are described in the PHP-CS-Fixer documentation, as is a way to 
create a configuration file that you can store in your repository.

## Finding Dependencies

In order to make sure you target the right version of PHP, and found all 
dependencies on PHP extensions you use in your code, it is important
to use PHP_CompatInfo. In this example we run it on the
[YubiTwee](https://github.com/fkooman/php-yubitwee/) code.

    $ phpcompatinfo analyser:run src

Here `src` is the directory to check, you may also want to check the `bin`, 
`tests` and `web` directories. It does not seem possible to specify multiple
paths at the same time.

At the bottom of the report you'll see something like this:

    Requires PHP 7.0.2 (min), PHP 7.0.2 (all)

This indicates PHP 7.0.2 is required, which is NOT good! Near the top you'll 
find `Extensions Analysis` which lists the extensions of PHP that we use in the 
code, in the case of [YubiTwee](https://github.com/fkooman/php-yubitwee/) that
is the following:

    Core              Core     5.1.0       5.1.0
    curl              curl     5.1.3       5.1.3
    date              date     5.2.0       5.2.0
    hash              hash     5.6.0beta1  5.6.0beta1
    pcre              pcre     4.0.0       4.0.0
    spl               spl      5.1.0       5.1.0
    standard          standard 7.0.2       7.0.2

All of them, except `Core` and `standard` can be added to the `composer.json` 
to tell Composer that those PHP extensions are required. It makes sense to look 
through the report carefully and make sure you didn't miss anything. If you
find the dependencies in the `bin`, `src` or `web` folders you add them to the
`require` section of `composer.json`, if you only find them in the `tests` 
folder you add them to the `require-dev` section. So, for YubiTwee the 
`require` section in `composer.json` looks like this:

    "require": {
        "ext-curl": "*",
        "ext-date": "*",
        "ext-hash": "*",
        "ext-pcre": "*",
        "ext-spl": "*",
        "paragonie/constant_time_encoding": "^1|^2",
        "paragonie/random_compat": "^1|^2",
        "php": ">=5.4",
        "symfony/polyfill-php56": "^1"
    }

To find out why we need PHP 7.0.2, we can use the report to search for the 
functions that require PHP 7:

    random_bytes             1       standard 7.0.2       7.0.2
    random_int               1       standard 7.0.2       7.0.2

It turns out these two functions are added in PHP 7. Fortunately we have a 
"polyfill" for it in `paragonie/random_compat` that takes care of this. This
makes those two functions available in PHP 5.4 as well!

    hash_equals              1       hash     5.6.0beta1  5.6.0beta1   

This function is only available in PHP >= 5.6, so we use the 
`symfony/polyfill-php56` dependency to provide this function. It provides 
constant time string comparison.

In addition, we also use constant time encoding functions for "Base64" and 
"Hex" that are provided through `paragonie/constant_time_encoding`.

To validate your `composer.json` you can use:

    $ composer validate
    ./composer.json is valid

To update the dependencies, and to check if all PHP extensions are actually
available on the system you are running `composer` on:

    $ composer update
    Loading composer repositories with package information
    Updating dependencies (including require-dev)
    Package operations: 0 installs, 2 updates, 0 removals
      - Updating symfony/yaml (v3.3.8 => v3.3.9): Loading from cache
      - Updating phpdocumentor/reflection-common (1.0 => 1.0.1): Loading from cache
    Writing lock file
    Generating autoload files

In the example above some updates were available and they were installed.

# Packagist

Using Packagist is great for development. It becomes very easy to add new 
dependencies to the software. But, it is for development only. 

It is a very bad idea to depend on Packagist for production environments as 
you'll create a "moving target". The `composer.lock` file takes care of some of
that problem, but not if the software disappears from the Git repository. This
happened a few times before with 
[left-pad](http://blog.npmjs.org/post/141577284765/kik-left-pad-and-npm) on
[npmjs](https://www.npmjs.com/).

This problem is solved by separately packaging all dependencies and putting 
them in the (same) repository. Then, no matter what happens to the upstream 
code, the software will remain available neatly packaged without any 
dependencies on the network. This also makes it possible to use a mirror of 
e.g. the OS package repositories and the software repository so the server 
running the software does not access the (public) network at all anymore 
increasing security and having better control of installing (OS) updates.

# Packaging

Next up is packaging. Of course you could run `composer install` in your 
application directory and package the whole thing up, call it "DevOps" and make
deploying it, and especially updating it, someone else's problem. Or maybe 
even your own. Why not make it easy by packaging the software? That way you get 
the same benefits as all other software packaged in the distribution you deploy 
on, mostly meaning easy of installation and update of the software and its 
components, maybe even only a small component.

Packaging PHP libraries and applications is actually pretty straight forward, 
as you only put the PHP files on this disk, no need to compile anything. The 
only thing you have to deal with is the PHP autoloader. Composer is not used 
for packaging, so there is no automatically generated autoloader anymore. 
Luckily there is a very simple 
[autoloader](https://github.com/php-fedora/autoloader) project that is being 
used in CentOS/EPEL and Fedora for this very purpose.

We'll create a YubiKey validator application that just accepts a YubiKey OTP 
and asks the YubiCo servers to validate it. It depends on a library that we 
will also package to show the complete flow.

We need to create two packages:

* [fkooman/yubitwee](https://github.com/fkooman/php-yubitwee); 
* [yubicheck](https://github.com/fkooman/yubicheck);

To create a "template" `spec` file, the file that describes how to create the
package do the following:

    $ rpmdev-setuptree

## Library

Libraries get named after their Composer name, typically they contains the 
"vendor" and the name of the library". In case of YubiTwee, the vendor is 
`fkooman` and the library name is `yubitwee`. In that case, the name of the 
RPM package becomes `php-fkooman-yubitwee`. 

    $ cd ${HOME}/rpmbuild/SPECS
    $ rpmdev-newspec php-fkooman-yubitwee

The `Requires` and `BuildRequires` are taken from the `composer.json` file, 
make sure they match.

**TODO**: specify version numbers of used PHP libraries!

A useful tool is `rpmdev-bumpspec` where you can update the package version, 
and add a new `%changelog` entry at the bottom.

If you are packaging libraries or software that hasn't been released yet you 
can use a special `Release` tag. Suppose you are working towards a 1.0 release, 
you can make `Version` already `1.0.0`, but then make the `Release` field 
contain `0.1%{?dist}`. Updating the package would then result in `0.2%{?dist}` 
indicating it is not the final version yet. Once `1.0.0` is release, the 
`Release` field would become `1%{?dist}`.

In the example below the `%global commit0` comes from the hash of the tag 
`1.1.0`.

The `php-fkooman-yubitwee.spec` file you end up with:

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

### Building
    
The next command will fetch the source code it place it in 
`${HOME}/rpmbuild/SOURCES`:

    $ spectool -g -R php-fkooman-yubitwee.spec

Creating the source RPM:

    $ rpmbuild -bs php-fkooman-yubitwee.spec

Building the "binary" RPM, in this case actually `noarch` as it is PHP:

    $ rpmbuild -bb php-fkooman-yubitwee.spec

The output RPM, ready to be installed, will be placed in 
`${HOME}/rpmbuild/RPMS/noarch`.

### Checking Packages

The `rpmlint` tool can be used to verify the spec-file, the source RPM and the 
package RPM:

    $ rpmlint php-fkooman-yubitwee.spec \
        ${HOME}/rpmbuild/SRPMS/php-fkooman-yubitwee-1.1.0-1.fc26.src.rpm \
        ${HOME}/rpmbuild/RPMS/noarch/php-fkooman-yubitwee-1.1.0-1.fc26.noarch.rpm 
    php-fkooman-yubitwee.src: W: spelling-error %description -l en_US pluggable -> plug gable, plug-gable, plugged
    php-fkooman-yubitwee.noarch: W: spelling-error %description -l en_US pluggable -> plug gable, plug-gable, plugged
    2 packages and 1 specfiles checked; 0 errors, 2 warnings.

There are no critical errors here, just something about a spelling 
disagreement.

### Mock

In order to make sure the package also builds on a clean installation, e.g. 
all required dependencies are installed it is important to build the package,
*and* run the tests on a clean system. The tool to use for that is
[Mock](https://github.com/rpm-software-management/mock/wiki). Make sure your 
user account is part of the `mock` group as shown in the Mock documentation.

To enable "nosync" to speed up builds a great deal:

    $ echo "config_opts['nosync'] = True" >> ${HOME}/.config/mock.cfg

To use Mock, you first need to generate the source RPM, as shown above and 
then run Mock. This will build on the platform that has the `default.cfg` 
pointed to in `/etc/mock`, probably the version of Fedora you are running:

    $ mock ${HOME}/rpmbuild/SRPMS/php-fkooman-yubitwee-1.1.0-1.fc26.src.rpm

To build for CentOS/Red Hat 7, we need to pass the `--yum` flag here:

    $ mock -r epel-7-x86_64 --yum ${HOME}/rpmbuild/SRPMS/php-fkooman-yubitwee-1.1.0-1.fc26.src.rpm

This will build the RPMs from scratch, and will also run the unit tests. Now 
you have a package for both CentOS and Fedora where the unit tests were 
actually ran on the platform you will deploy on!

## Web Application

The `yubicheck.spec` file you end up with:

    %global commit0 b5362b4fb627b274bc98a8140f99685a58a54c0f
    %global shortcommit0 %(c=%{commit0}; echo ${c:0:7})

    Name:           yubicheck
    Version:        1.0.1
    Release:        1%{?dist}
    Summary:        Simple YubiKey OTP checker for the Web

    License:        MIT
    URL:            https://github.com/fkooman/yubicheck
    Source0:        https://github.com/fkooman/yubicheck/archive/%{commit0}.tar.gz#/%{name}-%{shortcommit0}.tar.gz

    BuildArch:      noarch

    BuildRequires:  php(language) >= 5.4.0
    BuildRequires:  php-composer(fedora/autoloader)
    BuildRequires:  php-composer(fkooman/yubitwee)
    BuildRequires:  %{_bindir}/phpunit

    Requires:       php(language) >= 5.4.0
    Requires:       php-composer(fedora/autoloader)
    Requires:       php-composer(fkooman/yubitwee)

    %if 0%{?fedora} >= 21
    Requires:       php(httpd)
    %else
    # Fedora < 21 and CentOS/RHEL
    Requires:       httpd
    %endif

    %description
    Simple YubiKey OTP checker for the Web.

    %prep
    %autosetup -n %{name}-%{commit0}

    %build
    cat <<'AUTOLOAD' | tee src/autoload.php
    <?php
    require_once '%{_datadir}/php/Fedora/Autoloader/autoload.php';

    \Fedora\Autoloader\Autoload::addPsr4('fkooman\\YubiCheck\\', __DIR__);
    \Fedora\Autoloader\Dependencies::required(array(
        '%{_datadir}/php/fkooman/YubiTwee/autoload.php',
    ));
    AUTOLOAD

    %install
    mkdir -p %{buildroot}%{_datadir}/yubicheck
    mkdir -p %{buildroot}%{_sysconfdir}/httpd/conf.d
    cp -pr src web %{buildroot}%{_datadir}/yubicheck

    cat <<'HTTPD' | tee %{buildroot}%{_sysconfdir}/httpd/conf.d/%{name}.conf
    Alias /yubicheck /usr/share/yubicheck/web

    <Directory /usr/share/yubicheck/web>
        Require all granted
        #Require local

        RewriteEngine on
        RewriteBase /yubicheck
        RewriteCond %{REQUEST_FILENAME} !-f
        RewriteCond %{REQUEST_FILENAME} !-d
        RewriteRule ^ index.php [L,QSA]
    </Directory>
    HTTPD

    %check
    cat <<'AUTOLOAD' | tee tests/autoload.php
    <?php
    require_once '%{_datadir}/php/Fedora/Autoloader/autoload.php';

    \Fedora\Autoloader\Autoload::addPsr4('fkooman\\YubiCheck\\Tests\\', __DIR__);
    \Fedora\Autoloader\Dependencies::required(array(
        '%{buildroot}/%{_datadir}/yubicheck/src/autoload.php',
    ));
    AUTOLOAD

    %{_bindir}/phpunit tests --verbose --bootstrap=tests/autoload.php

    %files
    %license LICENSE
    %doc composer.json CHANGES.md README.md
    %{_datadir}/yubicheck
    %config(noreplace) %{_sysconfdir}/httpd/conf.d/%{name}.conf

    %changelog
    * Thu Sep 07 2017 François Kooman <fkooman@tuxed.net> - 1.0.1-1
    - update to 1.0.1
    - allow access to all by default instead of just local

    * Sat Aug 26 2017 François Kooman <fkooman@tuxed.net> - 1.0.0-1
    - initial package

## Mockchain

If you have multiple packages, and they depend on each other, you need to use
`mockchain` to make this work. Specify the source RPMs in the build order, so 
first the dependencies and then the packages depending on them!

    $ mockchain -r fedora-26-x86_64 ${HOME}/rpmbuild/SRPMS/php-fkooman-yubitwee-1.0.1-1.fc26.src.rpm ${HOME}/rpmbuild/SRPMS/yubicheck-1.0.1-1.fc26.src.rpm

For CentOS, `-m --yum` is needed here:

    $ mockchain -r epel-7-x86_64 -m --yum /home/fkooman/rpmbuild/SRPMS/php-fkooman-yubitwee-1.0.1-1.fc26.src.rpm /home/fkooman/rpmbuild/SRPMS/yubicheck-1.0.0-1.fc26.src.rpm

## Repository

It makes sense to create a repository with these RPM files to allow for easy
installation and providing updates that will then be automatically installed
when the server is updated using e.g. `yum update`. 

I'm using a small script that takes care of this. 
# Deployment

This section will describe deployment of the code on a server. This becomes 
very easy now as we have packages available that will make everything work 
right away. The deployment will be done on a CentOS server.

## PHP

    $ sudo yum -y install php-fpm httpd

Modern PHP is deployed using PHP-FPM and not `mod_php` anymore. To make things
work the same as on Fedora we use a `php.conf` file that's part of the 
`php-fpm` package in Fedora. It can be found 
[here](https://src.fedoraproject.org/rpms/php/blob/master/f/php.conf). Put this
in `/etc/httpd/conf.d/php.conf`.

The default PHP-FPM configuration on CentOS does not use a socket, but listens
on the network, modify this as well:

    $ sudo sed -i "s|^listen = 127.0.0.1:9000$|listen = /run/php-fpm/www.sock|" /etc/php-fpm.d/www.conf

Make everything start on boot:

    $ systemctl enable httpd
    $ systemctl enable php-fpm
    $ systemctl restart httpd
    $ systemctl restart php-fpm

## Apache & SSL

The SSL configuration is done in `/etc/httpd/conf.d/ssl.conf`. The
configuration is not quite up to date as can be seen when using tools like 
[Qualys SSL Server Test](https://www.ssllabs.com/ssltest/) or 
[SSL Decoder](https://ssldecoder.org/). To improve this, I used 
[Mozilla SSL Configuration Generator](https://mozilla.github.io/server-side-tls/ssl-config-generator/?server=apache-2.4.6&openssl=1.0.2k&hsts=yes&profile=modern). The link points
to the configuration for the version of Apache and OpenSSL in CentOS 7.4, the
latest version at time of writing.

The updated version I use, using the correct file system paths for CentOS, can
be found 
[here](https://github.com/eduvpn/documentation/blob/master/resources/ssl.conf). 
It does not contain a `<VirtualHost>` as I create those in separate files.

## Installation

You can copy the created RPM file now to the server and install it using 
`dnf install` or on CentOS `yum install`. Restart Apache again and you should 
be good to go!

# Resources

* http://enricozini.org/blog/2014/debian/debops/
* https://fedoraproject.org/wiki/Packaging:SourceURL
* https://fedoraproject.org/wiki/Packaging:PHP
* https://fedoraproject.org/wiki/SIGs/PHP/PackagingTips#Autoloader
* http://www.phpthewrongway.com/


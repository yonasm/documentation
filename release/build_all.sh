#!/bin/sh

#
# Mock https://fedoraproject.org/wiki/Using_Mock_to_test_package_builds
#
# user MUST be part of mock group:
#   $ sudo usermod -a -G mock myusername 
#

#
# Configuration
#

REPO_DIR=${HOME}/repo

# CentOS
MOCK_CONFIG=epel-7-x86_64
#MOCK_FLAGS="-m --yum"

# Fedora
#MOCK_CONFIG=fedora-rawhide-x86_64
#MOCK_CONFIG=fedora-27-x86_64
#MOCK_CONFIG=fedora-26-x86_64
MOCK_FLAGS=

PACKAGE_LIST=(\
    php-bacon-bacon-qr-code \
    php-christian-riesen-otp \
    php-fkooman-oauth2-client \
    php-fkooman-oauth2-server \
    php-fkooman-yubitwee \
    php-fkooman-secookie \
    vpn-lib-common \
    vpn-admin-portal \
    vpn-server-api \
    vpn-server-node \
    vpn-user-portal \
    php-saml-ds \
    php-json-signer \
)

rpmdev-setuptree

mkdir -p "${REPO_DIR}/RPMS/noarch"
mkdir -p "${REPO_DIR}/SRPMS"

# Create Source RPMs
SRPM_LIST=""
cd rpm || exit
cp ./*.conf ./*.cron ./*.patch "${HOME}/rpmbuild/SOURCES"
for f in "${PACKAGE_LIST[@]}"
do
    spectool -g -R "${f}".spec
    SRPM_FILE=$(rpmbuild -bs "${f}".spec | cut -d ':' -f 2)
    SRPM_LIST+=" $(basename ${SRPM_FILE})"
done

echo "Build in progress, this may take a long time..."

# Build RPMs
(
    cd "${HOME}/rpmbuild/SRPMS" || exit
    RESULT_DIR=$(mockchain -r "${MOCK_CONFIG}" ${MOCK_FLAGS} ${SRPM_LIST} | grep "results dir" | cut -d ':' -f 2 | xargs)
    cp ${RESULT_DIR}/*/*.src.rpm "${REPO_DIR}/SRPMS"
    cp ${RESULT_DIR}/*/*.noarch.rpm "${REPO_DIR}/RPMS/noarch"
)

(
    cd "${REPO_DIR}" || exit
    # Sign RPMs
    rpm --addsign RPMS/noarch/* SRPMS/*
)

# Create Repository
(
    cd "${REPO_DIR}" || exit
    createrepo_c .
)

# Create Archive
DATETIME=$(date +%Y%m%d%H%M%S)
(
    cd "${REPO_DIR}" || exit
    tar -czf "../rpmRepo-${DATETIME}.tar.gz" .
)

# Done

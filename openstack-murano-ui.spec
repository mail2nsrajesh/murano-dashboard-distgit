%{!?upstream_version: %global upstream_version %{version}%{?milestone}}
%global pypi_name murano-dashboard
%global mod_name muranodashboard

Name:           openstack-murano-ui
Version:        XXX
Release:        XXX
Summary:        The UI component for the OpenStack murano service
Group:          Applications/Communications
License:        ASL 2.0
URL:            https://github.com/openstack/%{pypi_name}
Source0:        https://tarballs.openstack.org/%{pypi_name}/%{pypi_name}-%{upstream_version}.tar.gz
BuildRequires:  gettext
BuildRequires:  git
BuildRequires:  openstack-dashboard
BuildRequires:  python-beautifulsoup4
BuildRequires:  python-devel
BuildRequires:  python-django-formtools
BuildRequires:  python-django-nose
BuildRequires:  python-mock
BuildRequires:  python-mox3
BuildRequires:  python-muranoclient
BuildRequires:  python-nose
BuildRequires:  python-openstack-nose-plugin
BuildRequires:  python-oslo-config >= 2:3.14.0
BuildRequires:  python-pbr >= 1.6
BuildRequires:  python-semantic-version
BuildRequires:  python-setuptools
BuildRequires:  python-testtools
BuildRequires:  python-yaql >= 1.1.0
Requires:       openstack-dashboard
Requires:       PyYAML >= 3.10
Requires:       python-babel >= 2.3.4
Requires:       python-beautifulsoup4
Requires:       python-django >= 1.8
Requires:       python-django-babel
Requires:       python-django-formtools
Requires:       python-iso8601 >= 0.1.11
Requires:       python-muranoclient >= 0.8.2
Requires:       python-oslo-log >= 3.11.0
Requires:       python-semantic-version
Requires:       python-six >= 1.9.0
Requires:       python-yaql >= 1.1.0
BuildArch:      noarch

%description
Murano Dashboard
Sytem package - murano-dashboard
Python package - murano-dashboard
Murano Dashboard is an extension for OpenStack Dashboard that provides a UI
for Murano. With murano-dashboard, a user is able to easily manage and control
an application catalog, running applications and created environments alongside
with all other OpenStack resources.

%package doc
Summary:        Documentation for OpenStack murano dashboard
BuildRequires:  python-sphinx
BuildRequires:  python-oslo-sphinx
BuildRequires:  python-reno

%description doc
Murano Dashboard is an extension for OpenStack Dashboard that provides a UI
for Murano. With murano-dashboard, a user is able to easily manage and control
an application catalog, running applications and created environments alongside
with all other OpenStack resources.
This package contains the documentation.

%prep
%autosetup -n %{pypi_name}-%{upstream_version} -S git
# Let RPM handle the dependencies
rm -rf {test-,}requirements.txt tools/{pip,test}-requires

%build
%py2_build
# Generate i18n files
pushd build/lib/%{mod_name}
django-admin compilemessages
popd
# generate html docs
export OSLO_PACKAGE_VERSION=%{upstream_version}
%{__python2} setup.py build_sphinx
# remove the sphinx-build leftovers
rm -rf doc/build/html/.{doctrees,buildinfo}

%install
%py2_install
mkdir -p %{buildroot}%{_datadir}/openstack-dashboard/openstack_dashboard/local/enabled
mkdir -p %{buildroot}%{_datadir}/openstack-dashboard/openstack_dashboard/local/local_settings.d
mkdir -p %{buildroot}/var/cache/murano-dashboard
# Enable Horizon plugin for murano-dashboard
cp %{_builddir}/%{pypi_name}-%{upstream_version}/muranodashboard/local/local_settings.d/_50_murano.py %{buildroot}%{_datadir}/openstack-dashboard/openstack_dashboard/local/local_settings.d/
cp %{_builddir}/%{pypi_name}-%{upstream_version}/muranodashboard/local/enabled/_*.py %{buildroot}%{_datadir}/openstack-dashboard/openstack_dashboard/local/enabled/

%check
export PYTHONPATH="%{_datadir}/openstack-dashboard:%{python2_sitearch}:%{python2_sitelib}:%{buildroot}%{python2_sitelib}"
%{__python2} manage.py test muranodashboard --settings=muranodashboard.tests.settings

%post
HORIZON_SETTINGS='/etc/openstack-dashboard/local_settings'
if grep -Eq '^METADATA_CACHE_DIR=' $HORIZON_SETTINGS; then
  sed -i '/^METADATA_CACHE_DIR=/{s#.*#METADATA_CACHE_DIR="/var/cache/murano-dashboard"#}' $HORIZON_SETTINGS
else
  sed -i '$aMETADATA_CACHE_DIR="/var/cache/murano-dashboard"' $HORIZON_SETTINGS
fi
%systemd_postun_with_restart httpd.service

%postun
%systemd_postun_with_restart httpd.service

%files
%license LICENSE
%doc README.rst
%{python2_sitelib}/muranodashboard
%{python2_sitelib}/murano_dashboard*.egg-info
%{_datadir}/openstack-dashboard/openstack_dashboard/local/local_settings.d/*
%{_datadir}/openstack-dashboard/openstack_dashboard/local/enabled/*
%dir %attr(755, apache, apache) /var/cache/murano-dashboard

%files doc
%license LICENSE
%doc doc/build/html

%changelog

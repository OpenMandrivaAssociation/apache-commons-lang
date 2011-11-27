
%global base_name       lang
%global short_name      commons-%{base_name}

Name:           apache-%{short_name}
Version:        2.6
Release:        5
Summary:        Provides a host of helper utilities for the java.lang API
License:        ASL 2.0
Group:          Development/Java
URL:            http://commons.apache.org/%{base_name}
Source0:        http://archive.apache.org/dist/commons/%{base_name}/source/%{short_name}-%{version}-src.tar.gz
Patch0:         0001-Make-source-version-1.3.patch
BuildArch:      noarch
BuildRequires:  java-devel >= 0:1.6.0
BuildRequires:  jpackage-utils >= 0:1.7.2
BuildRequires:  maven-site-plugin
BuildRequires:  maven
BuildRequires:  apache-commons-parent

Requires:       java >= 0:1.6.0
Requires:       jpackage-utils >= 0:1.6
Requires(post):    jpackage-utils
Requires(postun):  jpackage-utils


# This should go away with F-17
Provides:       jakarta-commons-lang = 0:%{version}-%{release}
Obsoletes:      jakarta-commons-lang <= 0:2.4

%description
The standard Java libraries fail to provide enough methods for
manipulation of its core classes. The Commons Lang Component provides
these extra methods.
The Commons Lang Component provides a host of helper utilities for the
java.lang API, notably String manipulation methods, basic numerical
methods, object reflection, creation and serialization, and System
properties. Additionally it contains an inheritable enum type, an
exception structure that supports multiple types of nested-Exceptions
and a series of utilities dedicated to help with building methods, such
as hashCode, toString and equals.

%package        javadoc
Summary:        API documentation for %{name}
Group:          Development/Java
Requires:       jpackage-utils

Obsoletes:      jakarta-%{short_name}-javadoc <= 0:2.4

%description    javadoc
%{summary}.

%prep
%setup -q -n %{short_name}-%{version}-src
%patch0 -p1
sed -i 's/\r//' *.txt

%build
mvn-local install javadoc:javadoc

%install

# jars
install -d -m 755 $RPM_BUILD_ROOT%{_javadir}
install -p -m 644 target/%{short_name}-%{version}.jar $RPM_BUILD_ROOT%{_javadir}/%{name}.jar
ln -sf %{name}.jar %{buildroot}%{_javadir}/%{short_name}.jar

# pom
install -d -m 755 $RPM_BUILD_ROOT%{_mavenpomdir}
install -pm 644 pom.xml $RPM_BUILD_ROOT%{_mavenpomdir}/JPP-%{short_name}.pom
%add_to_maven_depmap org.apache.commons %{short_name} %{version} JPP %{short_name}

# following line is only for backwards compatibility. New packages
# should use proper groupid org.apache.commons and also artifactid
%add_to_maven_depmap %{base_name} %{base_name} %{version} JPP %{short_name}

# Old depmap was wrong and this surfaced as a problem when building
# other packages
%add_to_maven_depmap %{short_name} %{short_name} %{version} JPP %{short_name}

# javadoc
install -d -m 755 $RPM_BUILD_ROOT%{_javadocdir}/%{name}
cp -pr target/site/apidocs/* $RPM_BUILD_ROOT%{_javadocdir}/%{name}

%pre javadoc
# workaround for rpm bug, can be removed in F-17
[ $1 -gt 1 ] && [ -L %{_javadocdir}/%{name} ] && \
rm -rf $(readlink -f %{_javadocdir}/%{name}) %{_javadocdir}/%{name} || :

%post
%update_maven_depmap

%postun
%update_maven_depmap

%files
%defattr(-,root,root,-)
%doc PROPOSAL.html LICENSE.txt RELEASE-NOTES.txt NOTICE.txt
%{_javadir}/*
%{_mavenpomdir}/JPP-%{short_name}.pom
%{_mavendepmapfragdir}/*

%files javadoc
%defattr(-,root,root,-)
%doc LICENSE.txt NOTICE.txt
%doc %{_javadocdir}/%{name}


%global base_name lang
%global short_name commons-%{base_name}

Name:		apache-%{short_name}
Version:	2.6
Release:	1
Summary:	Helper utilities for the java.lang API
Group:		Development/Java
License:	ASL 2.0
URL:		https://commons.apache.org/%{base_name}/
Source0:	https://archive.apache.org/dist/commons/%{base_name}/source/%{short_name}-%{version}-src.tar.gz
# LANG-719. Patterns of one or three 'Y's follow the Java 7 year rules.
Patch1:		0002-Fix-FastDateFormat-for-Java-7-behaviour.patch

BuildArch:	noarch
# Literal, so the first rpmbuild -bs records them before sysjar is installed.
BuildRequires:	maven
BuildRequires:	java-current-devel
BuildSystem:	maven
BuildOption(install):	--file-name %{short_name} --link %{name}

Provides:	jakarta-%{short_name} = %{version}-%{release}
Obsoletes:	jakarta-%{short_name} < %{version}-%{release}

%description
Commons Lang adds helper methods for the classes in java.lang:
string handling, numbers, reflection, and builders for equals,
hashCode and toString. Gradle 8.11.1 links commons-lang:commons-lang.

%prep
%autosetup -n %{short_name}-%{version}-src -p1
# org.apache.commons.lang.enum is a package name. javac rejects enum
# as an identifier. The supported API is org.apache.commons.lang.enums.
rm -rf src/main/java/org/apache/commons/lang/enum \
	src/test/java/org/apache/commons/lang/enum
# commons-parent 17 is rewritten onto a current parent, and that parent
# pulls moditect, which is not packaged. Coordinates are already set on
# this project. Entities.java is ISO-8859-1. JVMRandom.nextLong(long) is
# static and clashes with RandomGenerator, so compile against the Java 8 API.
python - <<'PY'
import xml.etree.ElementTree as ET

ET.register_namespace("", "http://maven.apache.org/POM/4.0.0")
ET.register_namespace("xsi", "http://www.w3.org/2001/XMLSchema-instance")

def local(tag):
    return tag.rsplit("}", 1)[-1]

tree = ET.parse("pom.xml")
root = tree.getroot()
ns = root.tag.split("}")[0] + "}" if root.tag.startswith("{") else ""
for child in list(root):
    if local(child.tag) == "parent":
        root.remove(child)
for parent in root.iter():
    for child in list(parent):
        if local(child.tag) != "plugin":
            continue
        artifact = next((c.text.strip() for c in child if local(c.tag) == "artifactId" and c.text), None)
        if artifact == "maven-assembly-plugin":
            parent.remove(child)
for prop in list(root):
    if local(prop.tag) != "properties":
        continue
    enc = rel = None
    for child in prop:
        name = local(child.tag)
        if name == "project.build.sourceEncoding":
            enc = child
        elif name == "maven.compiler.release":
            rel = child
    if enc is None:
        enc = ET.SubElement(prop, ns + "project.build.sourceEncoding")
    enc.text = "ISO-8859-1"
    if rel is None:
        rel = ET.SubElement(prop, ns + "maven.compiler.release")
    rel.text = "8"
tree.write("pom.xml", xml_declaration=True, encoding="unicode")
PY

%files -f .mfiles
%doc LICENSE.txt NOTICE.txt RELEASE-NOTES.txt

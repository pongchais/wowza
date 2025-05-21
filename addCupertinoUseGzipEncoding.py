import xml.etree.ElementTree as ET

xmlfile = "/usr/local/WowzaStreamingEngine/conf/p101aes/Application.xml"

parser = ET.XMLParser(target=ET.TreeBuilder(insert_comments=True))
tree = ET.parse(xmlfile, parser=parser)
root = tree.getroot()

def tag_without_namespace(tagstr):
    return tagstr.split('}', 1)[-1] if isinstance(tagstr, str) and '}' in tagstr else tagstr

def find_section(parent, name):
    """Find first direct child element with a given tag name (case-insensitive, ignoring comments)."""
    for c in parent:
        if not isinstance(c.tag, str):
            continue  # skip comments and such
        if tag_without_namespace(c.tag).lower() == name.lower():
            return c
    return None

# Improved indent function: closing tags at correct tab level
def indent(elem, level=0):
    i = "\n" + level * '\t'
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + '\t'
        for idx, child in enumerate(elem):
            indent(child, level+1)
            if idx == len(elem)-1:
                # Last child: align parent's closing tag properly
                if not child.tail or not child.tail.strip():
                    child.tail = i
            else:
                # Inner children: indent for next sibling
                if not child.tail or not child.tail.strip():
                    child.tail = i + '\t'
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = i

# If the root is not <Application>, find the <Application> child
if tag_without_namespace(root.tag).lower() == "application":
    application = root
else:
    application = find_section(root, "Application")
    if application is None:
        raise Exception("<Application> section not found!")

# Find or create the <HTTPStreamer>/<Properties> structure
httpstreamer = find_section(application, "HTTPStreamer")
if httpstreamer is None:
    raise Exception("<HTTPStreamer> section not found!")

properties = find_section(httpstreamer, "Properties")
if properties is None:
    properties = ET.SubElement(httpstreamer, "Properties")

# Check if the property already exists
found = False
for prop in properties.findall("Property"):
    name = prop.find("Name")
    if name is not None and name.text == "cupertinoUseGzipEncoding":
        found = True
        break

if not found:
    newprop = ET.Element("Property")
    n = ET.SubElement(newprop, "Name")
    n.text = "cupertinoUseGzipEncoding"
    v = ET.SubElement(newprop, "Value")
    v.text = "false"
    t = ET.SubElement(newprop, "Type")
    t.text = "Boolean"
    properties.append(newprop)
    print("Added cupertinoUseGzipEncoding property.")
    indent(root)  # Indent with tabs, closing tags aligned
    tree.write(
        xmlfile,
        encoding="utf-8",
        xml_declaration=True,
        short_empty_elements=False    # Use <tag></tag> not <tag/>
    )
else:
    print("Property already present; no changes made.")
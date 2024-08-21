import xml.etree.ElementTree as ET

class XMLToHTMLConverter:
    def __init__(self, xml_file, tag_mapping=None):
        self.xml_file = xml_file
        self.tree = ET.parse(self.xml_file)
        self.root = self.tree.getroot()
        self.tag_mapping = tag_mapping or {
            'Button': 'button',
            'TextView': 'div',
            'EditText': 'input',
            'Switch': 'input',
        }

    def convert(self):
        html_content = self._xml_to_html(self.root)
        return html_content

    def _xml_to_html(self, element):
        tag = self.tag_mapping.get(element.tag.split('.')[-1], 'div')
        class_name = element.tag.split('.')[-1]
        attributes = ' '.join([f'{k}="{v}"' for k, v in element.attrib.items() if k != 'text'])
        cursor_style = ''

        try:
            clickable = element.attrib['clickable'] == 'true'
            resource_id = element.attrib['resource-id']
            if clickable and resource_id:
                cursor_style = "style='cursor: pointer;'"
                class_name += ' clickable_attr'
        except KeyError:
            pass

        text = element.attrib.get('text', '')

        if tag == 'input':
            if element.tag.split('.')[-1] == 'Switch':
                attributes += ' type="checkbox"'
            else:
                attributes += ' type="text"'
        elif tag == 'img':
            attributes += f' src="{element.attrib.get("src", "")}"'

        children = ''.join([self._xml_to_html(child) for child in element])
        content = f'{text}{children}' if text else children
        end_tag = f'</{tag}>' 
        style = style=f"{cursor_style}" if cursor_style else ''
        return f'\n<{tag} class="ui_element {class_name}" {style} {attributes}>{content}{end_tag}\n'


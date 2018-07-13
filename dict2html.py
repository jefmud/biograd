from flask import abort
import collections
        
        
def generate_input(dict_object, key, hide, name, label=None, input_name=None):
    input_stack = ""
    
    if label is None:
        label = key

    prefix = '<div class="form-group">\n'
    postfix = '</div>\n'
    
    if input_name is None:
        name_str= '%s[%s]' % (name,key)
    else:
        name_str=input_name
        
    if key in hide:
        return
    if key == 'separator':
        return "<hr class='featurette-divider'>"
        
    elif isinstance(dict_object[key], str) or isinstance(dict_object[key], str):
        label_str = "<label for='%s'>%s</label>" % (name_str, label)
        input_str = "<input class='form-control' type='text' name='%s' value='%s'>" % (
            name_str, dict_object[key])
        input_stack += "%s%s\n%s\n%s" % (prefix, label_str, input_str, postfix)
    elif isinstance(dict_object[key], int):
        label_str = "<label for='%s'>%s</label>" % (name_str, label)
        input_str = "<input class='form-control' type='number' name='%s' value='%s'>" % (
            name_str, dict_object[key])
        input_stack += "%s%s\n%s\n%s" % (prefix, label_str, input_str, postfix)
    elif isinstance(dict_object[key], list):
        # this is a little different in that it is multiple inputs
        label_str = "<label for='%s'>%s</label>" % (name_str, label)
        input_str = ""
        for value in [item for item in enumerate(dict_object[key])]:
            input_str += "<input class='form-control' type='text' name='%s[%s]' value='%s'>" % (
                name_str, value[0], value[1])
        input_stack += "%s%s\n%s\n%s" % (prefix, label_str, input_str, postfix)
    elif isinstance(dict_object[key], dict):
        input_stack += "<div class='sub'>\n"
        input_stack += "<label>%s</label>" % (label)
        input_stack += generate_inputs(dict_object[key], hide, name=key)
        input_stack += "</div>\n"
    return input_stack


def generate_inputs(dict_object, hide, name):
    body = ""
    for key in dict_object.keys():
        body += generate_input(dict_object, key, hide, name)
    return body

def generate_inputs_from_schema(dict_object, schema, hide, name):
    """creates a series of inputs from dict_object, governed by the map_object (list of tuples)"""
    # each list element in the map_object
    body = ""
    for item in schema:
        label = item[1]
        key = item[0]
        try:
            # If a third element of the tuple is there, it is the input_name
            input_name=item[2]
        except:
            input_name=None
        body += generate_input(dict_object, key, hide, name, label, input_name)
    return body

def dict2form(dict_object, name="object", hide=[], method="get", xsrf=None, submit_name="Submit", ordered=True):
    if ordered:
        dict_object = collections.OrderedDict(sorted(dict_object.items(), key=lambda t: t[0]))
    head = "<form enctype='multipart/form-data' method='%s'>" % method
    body = "<input type='submit' value='%s'>" % (submit_name)
    bottom = "</form>"
    if xsrf:
        body += '<input type="hidden" name="_xsrf" value="%s"/>' % xsrf
    body = "%s%s" % (generate_inputs(dict_object, hide, name), body)
    result = "%s\n%s\n%s" % (head, body, bottom)
    return "%s\n%s\n%s" % (head, body, bottom)

def dict2form_schema(dict_object, schema=None, name="object", hide=[], method="get", xsrf=None, submit_name="Submit"):
    """creates FORM html from a dictionary object using a mapping object"""
    # map_object = [(dictionary_key,label,input_name),...]
    if schema is None:
        # hand-off to simpler treatment of dictionary
        return dict2form(dict_object, name=name, hide=hide, method=method, xsrf=xsrf, submit_name=submit_name)
    
    head = "<form enctype='multipart/form-data' method='%s'>" % method
    body = "<input type='submit' value='%s'>" % (submit_name)
    bottom = "</form>"
    
    if xsrf:
        body += '<input type="hidden" name="_xsrf" value="%s"/>' % xsrf
    body = "%s%s" % (generate_inputs_from_schema(dict_object, schema, hide, name), body)
    result = "%s\n%s\n%s" % (head, body, bottom)
    return "%s\n%s\n%s" % (head, body, bottom)    
    
def dict2html(dict_object,
              schema=None,
              template=None,
              template_prefix=None,
              template_postfix='<br />',
              output_prefix='',
              output_postfix='',
              hideblanks=False):
    """returns HTML from a dictionary, each key/value pair (typically) prints on a single line"""
    # using a schema will alter presentation order and label of dictionary.
    # schema is a LIST of tuples processed in order.  Each tuple contains (key,label)
    # a template is a python template format with TWO slots {}
    # each item is built from the template. e.g. template = "<td>{}</td><td>{}</td>"
    # each template item can have a template_prefix and a template_postfix e.g. template_prefix = "<tr>", template_postfix = "</tr>"
    # the output can have a output_prefix and output_postfix, e.g. output_prefix = "<table>" output_postfix = "</table>"
    content = []
    items = []
    if schema is None:
        for k, v in dict_object.items():
            items.append((k,k,v))
    else:
        # each item is done by schema order
        for schema_item in schema:
            items.append((schema_item[0], schema_item[1], dict_object.get(schema_item[0],'')))
            
    if template is None:
        template = "{}: {}"
    for item in items:
        if hideblanks and item[2]=='':
            continue
        if template_prefix:
            content.append(template_prefix)
        content.append(template.format(item[1],item[2]))
        if template_postfix:
            content.append(template_postfix)
    return output_prefix + '\n' + '\n'.join(content) + output_postfix
        
    
def dict2schema(dict_object):
    """makes a schema list from a dictionary, recall dictionaries have no order!"""
    # this will produce a very rough schema from a dictionary
    schema = []
    for k,v in dict_object.items():
        schema.append((k,k,v))
    return schema

def modal_wrapper(content, open_button="Open Modal",
                  name="myModal",
                  title="Modal Title",
                  footer_button="Close"):
    """modal helper function produces HTML to create a Bootstrap-4 compatible modal"""
    
    if footer_button:
        modal_footer_html = """
                        <div class="modal-footer">
                            <button type="button" class="btn btn-danger" data-dismiss="modal">{0}</button>
                        </div>
        """.format(footer_button)
    else:
        modal_footer_html = ""
    
    modal_template = """
    <!-- Button to Open the Modal -->
        <button type="button" class="btn btn-primary" data-toggle="modal" data-target="#{0}">
            {4}
        </button>
    
        <!-- The Modal -->
        <div class="modal" id="{0}">
            <div class="modal-dialog">
                <div class="modal-content">
    
                    <!-- Modal Header -->
                    <div class="modal-header">
                        <h4 class="modal-title">{1}</h4>
                        <button type="button" class="close" data-dismiss="modal">&times;</button>
                    </div>
    
                    <!-- Modal body -->
                    <div class="modal-body">
                        {2}
                    </div>
    
                    <!-- Modal footer -->
                    {3}
    
                </div>
            </div>
        </div>
    """.format(name, title, content, modal_footer_html, open_button)
    
    return modal_template
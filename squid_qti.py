# This module contains the qti functionality required for writing questiojns to canvas

import os
import re
import xml.etree.ElementTree as ET
import string
import random
from zipfile import ZipFile
from copy import deepcopy
from shutil import copyfile
from squid_utils import id_generator, get_img_filenames, get_filepaths, destroy

qti_template_string = r'''<?xml version="1.0" encoding="UTF-8"?>
<questestinterop xmlns="http://www.imsglobal.org/xsd/ims_qtiasiv1p2" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.imsglobal.org/xsd/ims_qtiasiv1p2 http://www.imsglobal.org/xsd/ims_qtiasiv1p2p1.xsd">
  <assessment ident="gb0ecfba78724dbfb528e1427f363a00d" title="Template 2">
    <qtimetadata>
      <qtimetadatafield>
        <fieldlabel>cc_maxattempts</fieldlabel>
        <fieldentry>1</fieldentry>
      </qtimetadatafield>
    </qtimetadata>
    <section ident="root_section">
      <item ident="gf8d22f497b786a1ae1d2fb34bfac7c25" title="Question 42">
        <itemmetadata>
          <qtimetadata>
            <qtimetadatafield>
              <fieldlabel>question_type</fieldlabel>
              <fieldentry>multiple_choice_question</fieldentry>
            </qtimetadatafield>
            <qtimetadatafield>
              <fieldlabel>points_possible</fieldlabel>
              <fieldentry>1.0</fieldentry>
            </qtimetadatafield>
            <qtimetadatafield>
              <fieldlabel>original_answer_ids</fieldlabel>
              <fieldentry>3971,1146,6934,4290</fieldentry>
            </qtimetadatafield>
            <qtimetadatafield>
              <fieldlabel>assessment_question_identifierref</fieldlabel>
              <fieldentry>g2f2fda5a18c54cf94e66cb5e04f892c4</fieldentry>
            </qtimetadatafield>
          </qtimetadata>
        </itemmetadata>
        <presentation>
          <material>
            <mattext texttype="text/html">&lt;div&gt;&lt;p&gt;Solve this multiple-choice question&lt;/p&gt;&lt;/div&gt;</mattext>
          </material>
          <response_lid ident="response1" rcardinality="Single">
            <render_choice>
              <response_label ident="3971">
                <material>
                  <mattext texttype="text/plain">Correct answer</mattext>
                </material>
              </response_label>
              <response_label ident="1146">
                <material>
                  <mattext texttype="text/plain">wrong answer 1</mattext>
                </material>
              </response_label>
              <response_label ident="6934">
                <material>
                  <mattext texttype="text/plain">wrong answer 2</mattext>
                </material>
              </response_label>
              <response_label ident="4290">
                <material>
                  <mattext texttype="text/plain">wrong answer 3</mattext>
                </material>
              </response_label>
            </render_choice>
          </response_lid>
        </presentation>
        <resprocessing>
          <outcomes>
            <decvar maxvalue="100" minvalue="0" varname="SCORE" vartype="Decimal"/>
          </outcomes>
          <respcondition continue="No">
            <conditionvar>
              <varequal respident="response1">3971</varequal>
            </conditionvar>
            <setvar action="Set" varname="SCORE">100</setvar>
          </respcondition>
        </resprocessing>
      </item>
      <item ident="gaf668087013dd5ee0780860dacfdfbe0" title="Question 69">
        <itemmetadata>
          <qtimetadata>
            <qtimetadatafield>
              <fieldlabel>question_type</fieldlabel>
              <fieldentry>file_upload_question</fieldentry>
            </qtimetadatafield>
            <qtimetadatafield>
              <fieldlabel>points_possible</fieldlabel>
              <fieldentry>1.0</fieldentry>
            </qtimetadatafield>
            <qtimetadatafield>
              <fieldlabel>original_answer_ids</fieldlabel>
              <fieldentry></fieldentry>
            </qtimetadatafield>
            <qtimetadatafield>
              <fieldlabel>assessment_question_identifierref</fieldlabel>
              <fieldentry>g0cc088b410b1d07f98c089f6f7d3d0ac</fieldentry>
            </qtimetadatafield>
          </qtimetadata>
        </itemmetadata>
        <presentation>
          <material>
            <mattext texttype="text/html">&lt;div&gt;&lt;p&gt;Solve this file-upload question.&lt;/p&gt;&lt;/div&gt;</mattext>
          </material>
        </presentation>
        <resprocessing>
          <outcomes>
            <decvar maxvalue="100" minvalue="0" varname="SCORE" vartype="Decimal"/>
          </outcomes>
        </resprocessing>
      </item>
    </section>
  </assessment>
</questestinterop>
'''

manifelt_template_string = r'''<?xml version="1.0" encoding="UTF-8"?>
<manifest identifier="g5cfd1114e1918b02ccdb0d2a1f8f03c8" xmlns="http://www.imsglobal.org/xsd/imsccv1p1/imscp_v1p1" xmlns:lom="http://ltsc.ieee.org/xsd/imsccv1p1/LOM/resource" xmlns:imsmd="http://www.imsglobal.org/xsd/imsmd_v1p2" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.imsglobal.org/xsd/imsccv1p1/imscp_v1p1 http://www.imsglobal.org/xsd/imscp_v1p1.xsd http://ltsc.ieee.org/xsd/imsccv1p1/LOM/resource http://www.imsglobal.org/profile/cc/ccv1p1/LOM/ccv1p1_lomresource_v1p0.xsd http://www.imsglobal.org/xsd/imsmd_v1p2 http://www.imsglobal.org/xsd/imsmd_v1p2p2.xsd">
  <metadata>
    <schema>IMS Content</schema>
    <schemaversion>1.1.3</schemaversion>
    <imsmd:lom>
      <imsmd:general>
        <imsmd:title>
          <imsmd:string>QTI Quiz Export for course "Florian Breuer's Sandbox Course"</imsmd:string>
        </imsmd:title>
      </imsmd:general>
      <imsmd:lifeCycle>
        <imsmd:contribute>
          <imsmd:date>
            <imsmd:dateTime>2021-10-13</imsmd:dateTime>
          </imsmd:date>
        </imsmd:contribute>
      </imsmd:lifeCycle>
      <imsmd:rights>
        <imsmd:copyrightAndOtherRestrictions>
          <imsmd:value>yes</imsmd:value>
        </imsmd:copyrightAndOtherRestrictions>
        <imsmd:description>
          <imsmd:string>Private (Copyrighted) - http://en.wikipedia.org/wiki/Copyright</imsmd:string>
        </imsmd:description>
      </imsmd:rights>
    </imsmd:lom>
  </metadata>
  <organizations/>
  <resources>
    <resource identifier="g341a25d4a2bd208b0312b0296f87c403" type="imsqti_xmlv1p2">
      <file href="g341a25d4a2bd208b0312b0296f87c403/g341a25d4a2bd208b0312b0296f87c403.xml"/>
    </resource>
    <resource identifier="g0620f8bf335314aee1c489df9d99fe10" type="webcontent" href="Uploaded Media/DF1-xy.png">
      <file href="Uploaded Media/DF1-xy.png"/>
    </resource>
  </resources>
</manifest>
'''

def qti_img_tags(s):
    '''
    Reformats any image tags in the string s with the right path for Canvas.
    Assumes these are local files, not urls!
    '''
    imgs = get_img_filenames(s)
    new_s = s
    for fn in imgs:
        new_s = new_s.replace(fn, '$IMS-CC-FILEBASE$/Uploaded%20Media/'+os.path.split(fn)[-1])
    return new_s

def qti_text(s):
    '''Reformats the strings s to make it suitable for QTI'''
    text = re.sub(r'\$(.*?)\$',r'\\(\1\\)',s)  # replace $?$ with \(?\) for MathJax
    text = qti_img_tags(text) # reformat image tags   ... will probably have to change a few more things...
    return text

def initialise_qti(title="Squid-based question pool", ident=None,  verbose=True):
    '''
    Initialise some globals, create a QTI assessment, return it in the form of an ElementTree.

    title : assessment title
    ident : assessment identifier. If None (default) then a random one is created.
    template_filement : the file used as template. Don't mess with this file unless you know what you're doing.
    verbose : if True (default), prints some messages.

    A global xml namespace is set for QTI and the following global variables are created:

    qti_template : ElementTree
    qti_root : the root element of qti_template
    qti_template_upload_question : Element
    qti_template_MCQ : Element
    ns : string containing namespace for qti xml file
    nsp : as above, but wrapped in {}
    '''
    global ns
    global nsp
    global qti_template
    global qti_root
    global qti_template_upload_question
    global qti_template_MCQ
    global qti_template_reponse
    # First, we set the correct xml namespaces
    ns = "http://www.imsglobal.org/xsd/ims_qtiasiv1p2"
    nsp = '{'+ns+'}'
    ET.register_namespace('', ns)
    ET.register_namespace('xsi', "http://www.w3.org/2001/XMLSchema-instance")
    # qti_template = ET.parse(template_filename) # Load the template from file
    qti_template = ET.ElementTree(ET.fromstring(qti_template_string))
    qti_root = qti_template.getroot() # the root of this tree
    for item in qti_root.findall(".//"+nsp+"item"): # Next, we extract templates for questions
        for l in item.findall(".//"+nsp+"qtimetadatafield"):
            if l.find(nsp+'fieldlabel').text == 'question_type':
                if l.find(nsp+'fieldentry').text == 'file_upload_question':
                    if verbose: print(f'Got the file upload question: {item.get("title")}')
                    qti_template_upload_question = deepcopy(item)
                if l.find(nsp+'fieldentry').text == 'multiple_choice_question':
                    if verbose: print(f'Got the multiple-choice question: {item.get("title")}')
                    qti_template_MCQ = deepcopy(item)
    # Now delete all items from the template, so what's left an empty assessment, ready for inserting new questions:
    for section in qti_root.findall(".//"+nsp+"section"):
        for item in section.findall(nsp+"item"):
            section.remove(item)
    qti_template_reponse = deepcopy(qti_template_MCQ.find(".//"+nsp+"response_label"))
    assessment = qti_root.find(".//"+nsp+"assessment")
    assessment.set('title', title)
    if ident is None:
        ident = 'g'+id_generator(size=30, chars='0123456789abcdef')
    assessment.set('ident', ident)
    return deepcopy(qti_template)

def qti_set_question_text(R, text):
    '''Given qti question R, changes the question text to text.'''
    R.find(".//"+nsp+"mattext").text = text

def qti_set_identifier(R, text):
    '''Given qti question R, changes the identifierref to text'''
    for l in R.findall(".//"+nsp+"qtimetadatafield"):
        if l.find(nsp+'fieldlabel').text == 'assessment_question_identifierref':
            l.find(nsp+'fieldentry').text = text

def qti_set_points(R, points):
    '''Given QTI question R, changes points to points.'''
    for l in R.findall(".//"+nsp+"qtimetadatafield"):
        if l.find(nsp+'fieldlabel').text == 'points_possible':
            l.find(nsp+'fieldentry').text = str(points)

def qti_file_upload_question_new():
    '''Returns a fresh copy of the file upload template'''
    return deepcopy(qti_template_upload_question)

def ET_file_upload_question(text='Question text',
                           a_q_id=None,
                           points=3,
                           ident=None,
                           title='Question 1'):
    '''Returns an ElementTree element containing a QTI file upload question. a_q_id and ident will be
    randomly generated unless given specific values'''
    Q = qti_file_upload_question_new() # create a new instance
    Q.set('title',title)
    if ident is None:
        ident = 'g'+id_generator(size=30, chars='0123456789abcdef')
    Q.set('ident', ident)
    qti_set_question_text(Q, text)
    if a_q_id is None:
        a_q_id = 'g'+id_generator(30)
    qti_set_identifier(Q, a_q_id)
    qti_set_points(Q, points)
    return Q

def qti_MCQ_new():
    '''Returns a fresh copy of the multiple-choice question template'''
    return deepcopy(qti_template_MCQ)

def ET_MCQ(text='Question text',
           a_q_id=None,
           points=1,
           ident=None,
           title='Question 1',
           answer='Correct answer',
           wrong_answers=['wrong answer 1', 'wrong answer 2', 'wrong answer 3'],
           none_of_these=True,
           shuffle_answers=True):
    '''
    Returns an ElementTree element containing a QTI multiple-choice question. a_q_id and ident will be
    randomly generated unless given specific values.

    To Do: randomise the answers (so you don't have to do so in Canvas, and "None of the above" is always last.)
    '''
    Q = qti_MCQ_new() # create a new instance
    Q.set('title',title)
    if ident is None:
        ident = 'g'+id_generator(size=30, chars='0123456789abcdef')
    Q.set('ident', ident)
    qti_set_question_text(Q, text)
    if a_q_id is None:
        a_q_id = 'g'+id_generator(30)
    qti_set_identifier(Q, a_q_id)
    qti_set_points(Q, points)
    answers = [answer]+wrong_answers
    if none_of_these:
        answers.append('None of the others')
    # Now generate the original_answer_ids. I'm not sure what happens if there is a collision of these
    # among different questions... but at least make sure no collisions happen within a question
    options = len(answers)
    answer_ids = list({id_generator(size=1, chars='123456789')+id_generator(size=3, chars='0123456789')
                       for k in range(options+2)})[:options]
    # write the list of answer_ids to the right place
    for l in Q.findall(".//"+nsp+"qtimetadatafield"):
        if l.find(nsp+'fieldlabel').text == 'original_answer_ids':
            l.find(nsp+'fieldentry').text = ','.join(answer_ids)
    # delete response_labels from template:
    render_choice = Q.find(".//"+nsp+"render_choice")
    for response_label in render_choice.findall(nsp+"response_label"):
        render_choice.remove(response_label)

    ordering = list(range(options))
    if shuffle_answers:
        if none_of_these:   # don't shuffle the last one around
            ordering = random.sample(ordering[:-1], len(ordering[:-1]))+[ordering[-1]]
        else:  # shuffle all of them
            ordering = random.sample(ordering, len(ordering))
    # now insert the various choices
    for k in ordering:
        response = deepcopy(qti_template_reponse)
        response.set('ident', answer_ids[k])
        qti_set_question_text(response, answers[k])
        render_choice.append(response)
    #
    # for k, text in enumerate(answers):
    #     response = deepcopy(qti_template_reponse)
    #     response.set('ident', answer_ids[k])
    #     qti_set_question_text(response, text)
    #     render_choice.append(response)
    # Finally, tell it which response is the correct one
    varequal = Q.find(".//"+nsp+"varequal")
    varequal.text = answer_ids[0]
    return Q

def qti_insert_question(Q, T=None):
    '''
    Inserts question Q into a qti assessment T, which should be of type ElementTree.
    If T is None, then the global qti_template is used.
    Returns T.
    '''
    if T is None:
        T = qti_template
    R = T.getroot()
    section = R.find(".//"+nsp+"section")
    section.append(Q)
    return T

def save_qti(filename, T=None, verbose=False, zip_it=True):
    '''
    Save the T to filename.
    T should be an ElementTree, not Element. Default: qti_template.
    filename should be the filename without extension.
    If zip_it is True (default), the result is two files: filename.xml and filename.zip,
    if zip_it is False, then only filename.xml is written.

    CAUTION: Does not include images or imsmanifest.xml
    '''
    if T is None:
        T = qti_template
    T.write(filename+'.xml', encoding='UTF-8', xml_declaration=True)
    if verbose:
        print(f'Created {filename}.xml')
    if zip_it:
        with ZipFile(filename+'.zip', 'w') as zipobj:
            zipobj.write(filename+'.xml')
        if verbose:
            print(f'Created {filename}.zip - You can upload this file to Canvas.')

def write_manifest(subdir, ident=None):
    '''Writes the imsmanifest.xml file into the directory subdir.
    If ident is None (default), then we obtain the assessment identifier by looking at the subdirectory'''

    if ident is None:   # look at the directory to see what the identifier is
        directorylist = os.listdir(subdir)
        try:
            directorylist.remove('Uploaded Media')
        except ValueError:
            pass
        ident = directorylist[0]

    # Now, register some namespaces and load the manifest templates
    # manifest_template_filename = 'imsmanifest_template.xml'
    ns = "http://www.imsglobal.org/xsd/imsccv1p1/imscp_v1p1"
    nsp = '{'+ns+'}'
    ET.register_namespace('', ns)
    ET.register_namespace('xsi', "http://www.w3.org/2001/XMLSchema-instance")
    ET.register_namespace('lom', "http://ltsc.ieee.org/xsd/imsccv1p1/LOM/resource")
    ET.register_namespace('imsmd', "http://www.imsglobal.org/xsd/imsmd_v1p2")
    manifest_template = ET.ElementTree(ET.fromstring(manifelt_template_string))
    # manifest_template = ET.parse(manifest_template_filename) # Load the template from file
    resource_template = deepcopy(manifest_template.find('.//'+nsp+"resource"))  # extract the resource template
    # now delete the resources:
    root = manifest_template.getroot()
    resource_root = root.find('.//'+nsp+"resources")
    for resource in list(resource_root):
        resource_root.remove(resource)

    # The templates are ready. Only now can we define the methods for using them.
    def new_resource():
        return deepcopy(resource_template)

    def resource_xml(ident):
        '''Returns the resource xml node for the main assessment file.
        ident is its identifier and also determines the filename'''
        r = new_resource()
        r.set('identifier', ident)
        r.set('type', "imsqti_xmlv1p2")
        file = r.find(nsp+'file')
        file.set('href', ident+'/'+ident+'.xml')
        return r

    def resource_img(filename, imgident=None):
        '''Returns the resource xml node for the image [filename].
        It gets an identifier imgident. If this is None (default), we invent a random one.'''
        if imgident is None:
            imgident = 'g'+id_generator(size=30, chars='0123456789abcdef')
        r = new_resource()
        r.set('identifier', imgident)
        r.set('type', "webcontent")
        r.set('href', "Uploaded Media/"+filename)
        file = r.find(nsp+'file')
        file.set('href', "Uploaded Media/"+filename)
        return r

    def insert_resource(R, T=None):
        '''Inserts the resource xml node R into the ElementTree T.'''
        if T is None:
            T = manifest_template
        resource_root = T.getroot().find('.//'+nsp+"resources")
        resource_root.append(R)
        return T

    # Finally, let's put everything together
    insert_resource(resource_xml(ident))
    try:
        for imgfile in os.listdir(os.path.join(subdir, "Uploaded Media")):
            insert_resource(resource_img(imgfile))
    except FileNotFoundError:
        pass
    manifest_template.write(os.path.join(subdir,'imsmanifest.xml'))

def SaveToQtiFile(L,
        zip_filename='upload_me_to_canvas',
        title='Squid-made question pool',
        subdir='Squid_pool',
        overwrite=False,
        clean_up=True,
        make_variant_numbers=True,
        verbose=False):
    '''
    Saves a list L of Squid questions to a qti file for uploading to canvas.
    filename should *exclude* the file extension.
    subdir is the subdirectory into which the various files will be written.
    If overwrite is True (default is False): delete existing zip_filename and subdir first.
    If clean_up is True (default is True): delete subdir afterwards.'''
    if os.path.exists(zip_filename+'.zip'):
        if overwrite:
            os.remove(zip_filename+'.zip')
        else:
            print(f'*** {zip_filename}.zip already exists! Use SaveToQtiFile(L, overwrite=True) to force deleting it first.')
            return
    if os.path.exists(subdir):
        if overwrite:
            destroy(subdir)
            os.mkdir(subdir)
        else:
            print(f'*** {subdir} already exists! Use SaveToQtiFile(L, overwrite=True) to force deleting it first.')
            return
    else:
        os.mkdir(subdir)
    images = []
    for Q in L:    # Populate a list of all image filenames used in questions in L
        images = images + get_img_filenames(Q.q_text())
        if Q.question_type == 'MCQ':
            images = images + get_img_filenames(Q.answer)
            for wa in Q.wrong_answers:
                images = images + get_img_filenames(wa)

    ident = 'g'+id_generator(size=30, chars='0123456789abcdef')  # the assessment identifier, also needed for filenames
    T = initialise_qti(title=title, ident=ident, verbose=False)
    if make_variant_numbers:
        for k,Q in enumerate(L):
            Q.update_variant_number(k+1)
    for Q in L:
        qti_insert_question(Q.qti(), T)

    if len(images) > 0:  # we also have images to worry about
        img_path = os.path.join(subdir, 'Uploaded Media')
        if not os.path.exists(img_path):
            os.mkdir(img_path)
        for img in images:  # now copy accross all the image files
            target = os.path.join(img_path, os.path.split(img)[-1])
    #         print(target)
            copyfile(img, target)
    assessment_path = os.path.join(subdir, ident)
    if not os.path.exists(assessment_path):
        os.mkdir(assessment_path)
    assessment_filename = os.path.join(assessment_path, ident+'.xml')
    T.write(assessment_filename, encoding='UTF-8', xml_declaration=True)

    write_manifest(subdir) # create the manifest file

    # now write the whole structure to a zip file:
    os.chdir(subdir)
    files = get_filepaths('.')
    with ZipFile(os.path.join('..',zip_filename+'.zip'), 'w') as zipobj:
        for file in files:
            zipobj.write(file)
    os.chdir('..')
    if verbose:
        print(f'Created {zip_filename}.zip. You can upload it to canvas.')
    if clean_up:
        destroy(subdir)

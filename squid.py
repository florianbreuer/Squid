# This is the main module for Squid. I'll write more later.
# Should contain Question classes and main methods.
#
# To do: (I hope I remember to keep this as my main todo list)
#
# * Update html2latex to handle tables (medium), images in urls (low)
#   * For this I must learn more html and css...
# * Fix Question_MCQ to correctly handle variable numbers of answers (high)
# * Write some nice Python Squid demos/tutorials (high), also for e.g. Physics
# * Set up Binder for Python Squid (high)
# * Figure out how to manage lots of question pools and save them to disk (medium)
# * Include marking rubrics in QTI files (medium)
# * nicen up the selection_wizard with better tooltips etc. (medium)
# * Implement more question types: computed answer (medium),
#     multiple selections (low), match answer (low), explore others (low)
# * Write better docsrtings (medium) with tests (low)
# * Wrap code to 79 columns (low)
#
# * Squid Ink: paper-based quizzes! (???)

import os
import pickle
import itertools
import random
import re
from zipfile import ZipFile
import ipywidgets as widgets
from IPython.display import FileLink
from squid_utils import (html2latex, get_img_filenames, get_filepaths,
    get_subdirs, destroy)
from squid_qti import (qti_text, ET_file_upload_question, ET_MCQ, SaveToQtiFile)

# Basic question types:

class Question_Base(object):
    '''Base class for questions. Contains methods and attributes common to all question types.
    Specific question types, such as Question_MCQ and Question_Written will be subclasses of this. '''
    points = 0
    variant_number = 0
    question_text = "there is no question text yet"
    question_text_basic = "there is no question text yet"
    solution_text = "no solution to no question"
    table_row = []
    table_header = []

    def q_text(self): # these can be rewritten when defining new questions
        return self.question_text

    def sol_text(self):
        return self.solution_text

    def update_variant_number(self, variant_number=None):
        '''Change the variant number, update question text accordingly'''
        if variant_number != None:
            self.variant_number = variant_number

    def __repr__(self):
        return(self.q_text())

    def latex_question_text(self):
        '''Returns self.question_text converted from html to latex.'''
        return(html2latex(self.q_text()))

    def _repr_html_(self):
        return(self.q_text())

class Question_Written(Question_Base):
    '''This is a written question.

    The most important methods are:
      self.q_text()   which returns the question as a string
      self.sol_text()   which returns the full solution as a string

    For backward compatibility, these methods also write their output to
    the attributes self.question_text and self.solution_text, respectively.
    The motivation for this slight change is to be able to update the variant
    number after initialising the question.

    It also contains summary data about the question to be included as a row in a LaTeX table of questions:
      self.table_header contains the headings for a table of question variants (e.g. question, answer).
      self.table_row contains the entries of a row containing this info.

    Various methods display this data, save the marking scheme to a .tex file, etc.
    '''
    def __init__(self, question_text='No question yet.', solution_text='No solution yet.', marks=3, variant_number=0):
        self.question_type = 'WAQ'
        self.question_text = question_text
        self.solution_text = solution_text
        self.marks = marks
        self.variant_number = variant_number
        self.rubric = r"""
    \noindent{\bf Marking Scheme:}
    \begin{small}
    \begin{itemize}
    \item 1 mark: The student demonstrates a partial understanding of how to do the problem.
    \item 2 marks: The student demonstrates a good understanding of how to do the problem \\ (some minor errors permitted).
    \item 3 marks: The student demonstrates a good understanding and obtains the correct answer.
    \end{itemize}
    \end{small}"""

    def q_text(self): # these can be rewritten when defining new questions
        self.update_variant_number()
        return self.question_text

    def update_variant_number(self, variant_number=None):
        '''Change the variant number, update question text accordingly'''
        if variant_number != None:
            self.variant_number = variant_number
        self.question_text = self.question_text_basic + "<br>[For office use only: V" + str(self.variant_number)+"]"

    def qti(self, variant_number=None, points=3, title=None):
        '''Return and ElementTree element representing this question, ready for inserting into a QTI assessment.
        if variant_number is None, the question's own variant number is used.'''
        if variant_number is not None:
            self.update_variant_number(variant_number)
        if title is None:
            title = f'Question {self.variant_number}'
        return ET_file_upload_question(text=qti_text(self.q_text()), points=points, title=title)

    def make_BB_row(self):
        '''Returns a row for writing self to a Blackboard file.
        This code owes much to Bjoern Rueffer.'''
        self.BB_question_text = self.q_text()
        self.BB_question_text = re.sub(r'\$\$(.*?)\$\$',r'\\[\1\\]',self.BB_question_text)
        self.BB_question_text = re.sub(r'\$(.*?)\$',r'\\(\1\\)',self.BB_question_text)
        self.BB_question_text = re.sub(r'\\dfrac\b',r'\\frac',self.BB_question_text)
        self.BB_question_text = re.sub('[\n ]+',' ',self.BB_question_text)
        return("FIL\t"+self.BB_question_text+"\n")


    def write_BB_row(self, f):  #f is a file that's already been opened for writing
        '''Writes the question in one line to file f (assumed to be open and writable) in the correct format for BlackBoard.
        '''
        f.write(self.make_BB_row())

    def latex_solution_page(self,var_number=-1):
        '''Returns a page for the marking scheme; var_number is an optional variant number '''
        if var_number==-1:
            var_number=self.variant_number  # i can be changed post-hoc in case variant_number wasn't initially supplied
        s = "\\newpage\n\\section{Variant "+str(var_number)+"}\n\\label{v"+str(var_number)+"}\n\n"+\
        self.latex_question_text()+"\n\\medskip\n\n"+r"\noindent{\bf Solution.}"+"\n\n"+self.sol_text()+"\n\\medskip\n\n"+self.rubric
        return(s)

    def test_solution_page(self,filename="test.tex",var_number=-1):
        '''Writes the solution page to a ready-to-compile LaTex file for testing'''
        with open(filename,'w') as f:
            f.write(r"\documentclass{article}"+"\n"+r"\usepackage{amssymb,amsmath,hyperref,a4wide}"+"\n\n"+r"\begin{document}"+"\n"+\
            self.latex_solution_page(var_number=var_number)+"\n"+r"\end{document}")

class Question_MCQ(Question_Base):
    """
    This class defines a multiple choice question.

    ATTRIBUTES:
        points : int
        answer : str
        wrong answers : List of str, most methods assume that there are exactly 3 wrong answers
               - I hope to change this in future
        question_text : str
        answer_shuffle : some permutation of [0,1,2,3] - used to print the answers in shuffled form
        answer_index : the index of the correct answer in the shuffled list - it's the index of 0 in answer_shuffle
        shuffle_seed : the random seed used for shuffling; intialised as randint(1,10000), optionally set in method shuffle()

        To do: improve shuffling, so it can take any number of wrong answers.


    """
    def __init__(self, question_text='No text yet', answer='', wrong_answers=[], marks=1, variant_number=0):
        self.question_type = 'MCQ'
        self.question_text = question_text
        self.answer = answer
        self.wrong_answers = wrong_answers
        self.marks = marks
        self.variant_number = variant_number
        self.answer_shuffle = [0,1,2,3]
        self.answer_index = 0
        self.shuffle_seed = 0

    def qti(self, variant_number=None, points=1, title=None):
        '''Return and ElementTree element representing this question, ready for inserting into a QTI assessment.
        if variant_number is None, the question's own variant number is used.'''
        if variant_number is not None:
            self.variant_number = variant_number
        if title is None:
            title = f'Question {self.variant_number}'
        # text = re.sub(r'\$(.*?)\$',r'\\(\1\\)',self.question_text) # turn $?$ into \( ?\)
        # text = qti_img_tags(text)   # modify image tags for Canvas
        return ET_MCQ(text=qti_text(self.question_text), points=points, title=title,
            answer=qti_text(self.answer), wrong_answers=[qti_text(m) for m in self.wrong_answers])


    def make_BB_row(self):
        '''Converts the question and answers into a a tuple of the format
        (MC, question, random_answer1, "correct/incorrect", ..., random_answer4, "correct/incorrect", "None of the others", "incorrect").

        The shuffling of the answers and the insertion of the last option is automatic and different
        in each invocation of this function. All formulas are escaped to play nicely with MathJax. All
        newlines are replaced with normal spaces, to comply with the format requirements of Blackboard.

        Code written by Bjoern Rueffer'''
        row = [self.question_text,self.answer,self.wrong_answers[0],self.wrong_answers[1],self.wrong_answers[2]]
        row = map(lambda s: re.sub(r'\$\$(.*?)\$\$',r'\\[\1\\]',s), row)
        row = map(lambda s: re.sub(r'\$(.*?)\$',r'\\(\1\\)',s), row)
        #row = map(lambda s: re.sub(r'\\displaystyle\b',r' ',s), row)
        row = map(lambda s: re.sub(r'\\dfrac\b',r'\\frac',s), row)
        row = map(lambda s: re.sub('[\n ]+',' ',s), row)
        question, *answers = tuple(row)
        answers = list(zip(answers, ('correct',*('incorrect',)*3)))
        random.shuffle(answers)
        answers = itertools.chain(*answers)
        answers = list(answers)
        return ('MC',question, *answers, 'None of the others', 'incorrect')

    def write_BB_row(self, f):  #f is a file that's already been opened for writing
        '''Writes the question in one line to file f (assumed to be open and writable) in the correct format for BlackBoard'''
        f.write("\t".join(self.make_BB_row())+"\n")

    def latex_sorted(self):
        '''Returns LaTex code that typsets the question and answers. Correct answer listed first.
        Currently only works for 3 wrong answers...'''
        return html2latex(self.q_text())+"\n\\begin{enumerate}\n  \\item %s \n  \\item %s \n"%(self.answer,self.wrong_answers[0])+\
    "  \\item %s \n  \\item %s \n  \\item None of the others \n\\end{enumerate}"%(self.wrong_answers[1], self.wrong_answers[2])

    def shuffle(self, s=0):
        '''Shuffles the four answers, using the random seed self.shuffle_seed, which can be set by the optional parameter s.'''
        if s!=0:
            self.shuffle_seed = s
            random.seed(s)
        else:
            self.shuffle_seed = 0
        self.answer_shuffle = [0,1,2,3]
        random.shuffle(self.answer_shuffle)
        # random.seed()  # reset the random number generator!
        self.answer_index = self.answer_shuffle.index(0)
        # i=1
        # for a in self.answer_shuffle:
        #     if a==0: self.answer_index = i
        #     i+=1

    def latex_shuffled(self):
        '''Returns LaTex code that typsets the question and answers.
        Answers are listed in the order determined by self.answer_shuffle'''
        answers = [self.answer]+self.wrong_answers
        answers = [answers[x] for x in self.answer_shuffle]
        return html2latex(self.q_text())+"\n\\begin{enumerate}\n  \\item[A.] %s \n  \\item[B.] %s \n"%(answers[0],answers[1])+\
    "  \\item[C.] %s \n  \\item[D.] %s \n  \\item[E.] None of the others \n\\end{enumerate}"%(answers[2], answers[3])

    def has_distinct_answers(self):
        '''Returns true if all answers are distinct.'''
        answers = [self.answer]+self.wrong_answers
        return len(answers)==len(set(answers))

    def _repr_html_(self):
        s=self.q_text()+r"<br><ol>"+\
        "\n".join([r"<li>"+a+r"</li>" for a in [self.answer]+self.wrong_answers+["None of these"]])+\
        r"</ol>"
        return(s)

# Next: Pool handling: save, load, displat etc question pools??

def SaveToBBfile(L, filename):
    '''Saves a list L of questions to a file for uploading to Blackboard.'''
    with open(filename,'w') as f:
        for Q in L:
            Q.write_BB_row(f)

def save_pool(pool, filename, zip_it=True, clean_up=False):
    '''
    Save the question pool to filename (a string without file extension).
    NOTE: Currently pool is assumed to be a list of questions!
    The pool is saved to a pickle file.
    If zip_it is True, make a zipfile including the pickle file and all images.
    If clean_up is True and zip_it is True, delete the pickle file.

    CAUTION: Pickle doesn't save the class definitions, so you need to somehow
    keep these, too!
    '''
    with open(filename+'.pickle', 'wb') as f:
        pickle.dump(pool, f)
    if zip_it:
        images = []
        for Q in pool:    # Populate a list of all image filenames used in questions in L
            images = images + get_img_filenames(Q.q_text())
            if Q.question_type == 'MCQ':
                images = images + get_img_filenames(Q.answer)
                for wa in Q.wrong_answers:
                    images = images + get_img_filenames(wa)
        with ZipFile(filename+'.zip', 'w') as zipobj:
            zipobj.write(filename+'.pickle')
            if len(images) > 0:  # also add the image files to the zipfile
                for img in images:
                    zipobj.write(img)
        if clean_up:
            os.remove(filename+'.pickle')

def load_pool(filename, update_to='None', clean_up=False):
    '''
    Returns the pool in filename (with extension).
    If it is a pickle file, unpickle it.
    If it is a zip file, extract all, then unpickle.
    If update_to = 'MCQ': update all questions to the latest Question_MCQ
    If update_to = 'WAQ': update all questions to the latest Question_Written

    WARNING: pickle doesn't actually save the type of an object, so this thing
    actually doesn't work. Must figure out how to persistently save objects...
    perhpas json it's code?? Use dill?
    '''
    base_filename, exp = os.path.splitext(filename)
    if exp.lower() == '.zip':  # we have a zipfile
        with ZipFile(filename, 'r') as zipobj:
            zipobj.extractall()
    with open(base_filename+'pickle', 'rb') as f:
        pool = pickle.load(f)
    if clean_up:
        os.remove(base_filename+'.pickle')
    if update_to == 'MCQ':
        return [update_MCQ(Q) for Q in pool]
    elif update_to == 'WAQ':
        return [update_written(Q) for Q in pool]
    else:
        return pool

def PrintMarkingScheme(L, course="MATH1120 2020 S2 ", title="", print_table=True, array_stretch=1):
    '''Prints a marking scheme for the list L of written-answer questions'''
    print(r"\documentclass{article}")
    print(r"\usepackage{amssymb,amsmath,hyperref,a4wide,graphicx}")
    print()
    print(r"\begin{document}")
    if array_stretch != 1:
        print(r"\renewcommand{\arraystretch}{"+str(array_stretch)+"}")
    print(r"\setcounter{page}{0}")
    print(course+title)  # e.g. "MATH1120 - 2020 - Workshop Week 3"
    print()
    print(r"Marking scheme for written-answer question")
    print()
    if print_table:
        print(r"\setcounter{section}{-1}")
        print(r"\section{Variant List}")
        print()
        cols = len(L[0].table_row)  # number of columns, excluding first column
        print(r"\medskip")
        print(r"\begin{tabular}{|l|"+"".join(["l|" for i in range(cols)])+"}")
        print(r"\hline")
        print(r"Variant & "+" & ".join(L[0].table_header)+r"\\ \hline")
        i=0
        for Q in L:
            i+=1
            if Q.variant_number>0:
                j=Q.variant_number
            else:
                j=i
            print(r"\hyperref[v"+str(j)+r"]{Variant "+str(j)+r"} & "+" & ".join(Q.table_row)+r"\\ \hline")
        print(r"\end{tabular}")
    print()
    print(r"\medskip")
    print(r"\begin{small}")
    print(r"\begin{itemize}")
    print(r"  \item 1 mark: The student demonstrates a partial understanding of how to do the problem.")
    print(r"  \item 2 marks: The student demonstrates a good understanding of how to do the problem \\ (some minor errors permitted).")
    print(r"  \item 3 marks: The student demonstrates a good understanding and obtains the correct answer.")
    print(r"\end{itemize}")
    print(r"\end{small}")
    i=0
    for Q in L:
        i+=1
        if Q.variant_number>0:
            print(Q.latex_solution_page())
        else:
            print(Q.latex_solution_page(i))
    print(r"\end{document}")

def TypesetMarkingScheme(L, course="MATH1120 2020 S2 ", title="", print_table=True, array_stretch=1, two_cols=False):
    '''Returns a marking scheme for the list L of written-answer questions'''
    s=r"\documentclass{article}"+"\n"+\
    r"\usepackage{amssymb,amsmath,hyperref,a4wide,longtable,graphicx}"+"\n\n"+\
    r"\begin{document}"
    if array_stretch != 1:
        s+=r"\renewcommand{\arraystretch}{"+str(array_stretch)+"}"
    s+=r"\setcounter{page}{0}"+"\n"+\
    r"{\Large "+course+" "+title+r"}"+"\n\n"+\
    r"Marking scheme for written-answer question"+"\n\n"

    if print_table:
        s+=r"\setcounter{section}{-1}"+"\n\n"+\
        r"\section{Variant List}"+"\n\n"
        cols = len(L[0].table_row)  # number of columns, excluding first column
        s+=r"\medskip"+"\n"
        if two_cols:  # the table would be too long, make two entries per table row
            s=s+r"\begin{longtable}{|l|"+"".join(["l|" for i in range(cols)])+"|l|"+"".join(["l|" for i in range(cols)])+"}"+\
            r"\hline"+"\n"+\
            r"Variant & "+" & ".join(L[0].table_header)+ r"& Variant & "+" & ".join(L[0].table_header)+ r"\\ \hline"+"\n"
            for i in range(0,len(L),2):
                Q = L[i]
                if Q.variant_number>0:
                    j = Q.variant_number
                else:
                    j = i
                s += r"\hyperref[v"+str(j)+r"]{Variant "+str(j)+r"} & "+" & ".join(Q.table_row)
                if i < len(L)-1:
                    Q = L[i+1]
                    if Q.variant_number>0:
                        j = Q.variant_number
                    else:
                        j = i+1
                    s += r"& \hyperref[v"+str(j)+r"]{Variant "+str(j)+r"} & "+" & ".join(Q.table_row)+r"\\ \hline"+"\n"
                else:
                    s += "& & "+"&".join(' ' for entry in Q.table_row)+r"\\ \hline"+"\n"
        else: # make a single table
            s=s+r"\begin{longtable}{|l|"+"".join(["l|" for i in range(cols)])+'}\n'+\
            r"\hline"+"\n"+\
            r"Variant & "+" & ".join(L[0].table_header)+r"\\ \hline"+"\n"
            i=0
            for Q in L:
                i+=1
                if Q.variant_number>0:
                    j=Q.variant_number
                else:
                    j=i
                s+=r"\hyperref[v"+str(j)+r"]{Variant "+str(j)+r"} & "+" & ".join(Q.table_row)+r"\\ \hline"+"\n"
        s+=r"\end{longtable}"+"\n\n"
    s+=r"\medskip"+"\n"
    s+=L[0].rubric+"\n\n"
    i=0
    for Q in L:
        i+=1
        if Q.variant_number>0:
            s+=Q.latex_solution_page()+"\n\n"
        else:
            s+=Q.latex_solution_page(i)+"\n\n"
    s+=r"\end{document}"
    return(s)

def SaveMarkingScheme(L, filename, course="MATH1120 2020 S2 ", title="", print_table=True, array_stretch=1, two_cols=False):
    '''Writes the marking scheme for the list L of questions to filename.'''
    with open(filename,'w') as f:
        f.write(TypesetMarkingScheme(L,course=course,
                                    title=title,
                                    print_table=print_table,
                                    array_stretch=array_stretch,
                                    two_cols=two_cols))

def selection_wizard(L,
                    course_name='MATH1120-LS-2022',
                    quiz_name='W2',
                    question_name='CA7_ClassifyCrit_MCQ_img'):
    '''Runs the selection Wizard to select questions from L, write to file, etc.
    Here L is a list of Squid questions, i.e. either Question_written or Question_MCQ.
    Ideally, all questions should be of the same class.'''
    b = 0
    L_selected = []
    items = [widgets.ToggleButton(description="variant "+str(i), button_style='') for i in range(len(L))]
    master = widgets.VBox([widgets.HBox(
        [items[i], widgets.HTMLMath(value="   :   ".join([a for a in L[i].table_row]))]) for i in range(len(L))])
    display(master)
    # widgets.Label(value=str([c.value for c in items]))
    out = widgets.Output(layout={'border': '1px solid black'}, description='Status:')

    Button_Count = widgets.Button(description="Count: ")
    def Count(b):
        count=0
        for c in items:
            if c.value:
                count += 1
        Button_Count.description = "Count: "+str(count)
    Button_Count.on_click(Count)

    Button_SelectAll = widgets.Button(description="Select All")
    def SelectAll(b):
        for c in items:
            c.value = True
        Button_Count.description = "Count: "+str(len(L))
    Button_SelectAll.on_click(SelectAll)

    Button_SelectNone = widgets.Button(description="Select None")
    def SelectNone(b):
        for c in items:
            c.value = False
        Button_Count.description = "Count: 0"
    Button_SelectNone.on_click(SelectNone)

    Button_MakeSelection = widgets.Button(description="Make Selection")
    def MakeSelection(b):
        nonlocal L_selected
        L_selected = []
        count = 0
        for i in range(len(L)):
            if items[i].value:
                count += 1
                Q = L[i]
                Q.update_variant_number(count)
                L_selected.append(Q)

        Button_Count.description="Count: "+str(count)
        with out:
            print("Selected %d Questions:"%count, [i for i in range(len(L)) if items[i].value])

    Button_MakeSelection.on_click(MakeSelection)

    Button_ClearOutput = widgets.Button(description="Clear Output")
    def ClearOutput(b):
        out.clear_output()
    Button_ClearOutput.on_click(ClearOutput)

    MarkingSchemeFilename = widgets.Text(value=course_name+'-'+quiz_name+"-MarkingScheme.tex",
                                         description='Filename:')

    MarkingSchemeArrayStretch = widgets.FloatText(value=1.5,step=0.1, description='Baseline_stretch:')

    BBFilename = widgets.Text(value=question_name+".txt", description='BB filename:')

    QTIFilename = widgets.Text(value=question_name, description='QTI filename:', tooltip='without file extension')

    QTITitle = widgets.Text(value=question_name, description="QTI title:")

    QTIsubdir = widgets.Text(value='Squid_pool', description="Working directory:")

    QTIoverwrite = widgets.Checkbox(value=True, description='overwrite')

    QTIcleanup = widgets.Checkbox(value=True, description='clean up')

    Path = widgets.Text(value="",description="File path:")

    CourseName = widgets.Text(value=course_name, description="Course:")

    QuizTitle = widgets.Text(value=quiz_name, description="Quiz:")

    MSPrintTable = widgets.Checkbox(value=True, description="Print table:")

    MakeTwoColumn = widgets.Checkbox(value=False, description="2 column table:")

    Button_SaveMarkingScheme = widgets.Button(description="Save Marking Scheme")
    def SaveMarkingSchemeB(b):
        MakeSelection(b)
        if len(L_selected) == 0:
            with out:
                print('No variants selected!')
            return
        if len(Path.value) > 0:
            fn = os.path.join(Path.value, MarkingSchemeFilename.value)
        else:
            fn = MarkingSchemeFilename.value
        SaveMarkingScheme(L_selected, filename=fn, course=CourseName.value, title=QuizTitle.value,
                          print_table=MSPrintTable.value, array_stretch=MarkingSchemeArrayStretch.value,
                          two_cols=MakeTwoColumn.value)
        with out:
            print('Marking scheme for variants', [i for i in range(len(L)) if items[i].value],' saved to ',fn)
            local_file = FileLink(fn)
            display(local_file)
    Button_SaveMarkingScheme.on_click(SaveMarkingSchemeB)

    Button_PrintMarkingScheme = widgets.Button(description="Print Marking Scheme")
    def PrintMarkingSchemeB(b):
        MakeSelection(b)
        if len(L_selected) == 0:
            with out:
                print('No variants selected!')
            return
        with out:
            print('Marking Scheme:')
            print()
            print(TypesetMarkingScheme(L_selected, course=CourseName.value, title=QuizTitle.value,
                                       array_stretch=MarkingSchemeArrayStretch.value,
                                       two_cols=MakeTwoColumn.value))
    Button_PrintMarkingScheme.on_click(PrintMarkingSchemeB)

    Button_SaveBB = widgets.Button(description="Save Blackboard file")
    def SaveBBFile(b):
        MakeSelection(b)
        if len(L_selected) == 0:
            with out:
                print('No variants selected!')
            return
        if len(Path.value) > 0:
            fn = os.path.join(Path.value, BBFilename.value)
            # fn=Path.value+"\\"+BBFilename.value    # This doesn't work for some reason
        else:
            fn = BBFilename.value
        SaveToBBfile(L_selected, fn)
        with out:
            print('BB entries for variants',[i for i in range(len(L)) if items[i].value],' saved to ',fn)
            local_file = FileLink(fn)
            display(local_file)
    Button_SaveBB.on_click(SaveBBFile)

    Button_SaveQTI = widgets.Button(description="Save QTI file")
    def SaveQTIFile(b):
        MakeSelection(b)
        if len(L_selected) == 0:
            with out:
                print('No variants selected!')
            return
        if len(Path.value) > 0:
            # fn=Path.value+"\\"+QTIFilename.value
            fn = os.path.join(Path.value, QTIFilename.value)
        else:
            fn = QTIFilename.value
        SaveToQtiFile(L_selected, zip_filename=fn, title=QTITitle.value,
                      subdir = QTIsubdir.value, overwrite=QTIoverwrite.value, clean_up=QTIcleanup.value,
                      verbose=False)
        with out:
            print(f'Variants {[i for i in range(len(L)) if items[i].value]} saved to {fn}.zip.')
            print('You can upload this to Canvas.')
            local_file = FileLink(fn+'.zip')
            display(local_file)
    Button_SaveQTI.on_click(SaveQTIFile)

    Button_PreviewQuestions = widgets.Button(description="Preview Selected Questions")
    def PreviewQuestions(b):
        MakeSelection(b)
        if len(L_selected) == 0:
            with out:
                print('No variants selected!')
            return
        with out:
            for Q in L_selected:
                display(Q)
    Button_PreviewQuestions.on_click(PreviewQuestions)

    Button_PrintBBRows = widgets.Button(description="Print BB Rows")
    def PrintBBRows(b):
        MakeSelection(b)
        if len(L_selected) == 0:
            with out:
                print('No variants selected!')
            return
        with out:
            for Q in L_selected:
                print(Q.make_BB_row())
    Button_PrintBBRows.on_click(PrintBBRows)

    SelectRange = widgets.IntRangeSlider(
        value=[0, len(L)-1],
        min=0,
        max=len(L)-1,
        step=1,
        description='Select range:',
        disabled=False,
        continuous_update=False,
        orientation='horizontal',
        readout=True,
        readout_format='d',
    )

    SavePoolcleanup = widgets.Checkbox(value=True, description="cleanup")
    SavePoolzipit = widgets.Checkbox(value=True, description="zip it")
    SavePoolfilename = widgets.Text(value='Pool-'+question_name, description="Pool file:")

    Button_SavePool = widgets.Button(description="Save selected")
    def SavePool(b):
        MakeSelection(b)
        if SavePoolzipit.value:
            fn = SavePoolfilename.value+'.zip'
        else:
            fn = SavePoolfilename.value+'.pickle'
        with out:
            save_pool(L, filename=SavePoolfilename.value, zip_it=SavePoolzipit.value, clean_up=SavePoolcleanup.value)
            print(f'Questions {[i for i in range(len(L)) if items[i].value]} saved to {fn}.')
    Button_SavePool.on_click(SavePool)

    Button_SelectAdd = widgets.Button(description="Add")
    def SelectAdd(b):
        for i in range(SelectRange.value[0],SelectRange.value[1]+1):
            items[i].value = True
        Count(b)
    Button_SelectAdd.on_click(SelectAdd)

    Button_SelectRemove = widgets.Button(description="Remove")
    def SelectRemove(b):
        for i in range(SelectRange.value[0],SelectRange.value[1]+1):
            items[i].value = False
        Count(b)
    Button_SelectRemove.on_click(SelectRemove)

    Button_SelectInvert = widgets.Button(description="Invert")
    def SelectInvert(b):
        for i in range(SelectRange.value[0],SelectRange.value[1]+1):
            items[i].value = not items[i].value
        Count(b)
    Button_SelectInvert.on_click(SelectInvert)

    Selector_MasterMode = widgets.Dropdown(options=['Table Row','Question Preview'], value='Table Row',
                                         description='Display Mode')


    def on_change_master_mode(change):
        if change['new'] == 'Table Row':
            for i in range(len(L)):
                master.children[i].children[1].value="   :   ".join([a for a in L[i].table_row])
        elif change['new'] == 'Question Preview':
            for i in range(len(L)):
                master.children[i].children[1].value = L[i].q_text()
        else:
            for i in range(len(L)):
                master.children[i].children[1].value = L[i].q_text()+'<br>'+\
                '<ol><li>'+L[i].answer+' (correct)'+\
                '</li><li>'+'</li><li>'.join(L[i].wrong_answers)+'</li></ol>'
    Selector_MasterMode.observe(on_change_master_mode, names="value")


    tab=widgets.Tab()
    tab.children=[widgets.VBox([widgets.HBox([SelectRange, Button_SelectAdd, Button_SelectRemove, Button_SelectInvert]),
                                widgets.HBox([SavePoolfilename, SavePoolzipit, SavePoolcleanup]),
                                Button_SavePool
                               ]),
                  widgets.VBox([MarkingSchemeFilename,
                                QuizTitle,
                                widgets.HBox([MSPrintTable, MakeTwoColumn]),
                                MarkingSchemeArrayStretch,
                                widgets.HBox([Button_PrintMarkingScheme,Button_SaveMarkingScheme])
                               ]),
                  widgets.VBox([widgets.HBox([QTIFilename, QTITitle, QTIsubdir]),
                               widgets.HBox([Button_SaveQTI, QTIoverwrite, QTIcleanup])
                               ]),
                  widgets.VBox([BBFilename,
                                widgets.HBox([Button_PrintBBRows,Button_SaveBB])
                               ]),
                  widgets.VBox([CourseName,
                                QuizTitle,
                                Path,
                                Selector_MasterMode,
                               ])
                 ]
    tab.set_title(index=0, title='Selection')
    tab.set_title(index=1, title='Marking scheme')
    tab.set_title(index=2, title='QTI (Canvas)')
    tab.set_title(index=3, title='Blackboard')
    tab.set_title(index=4, title='Options')

    display(widgets.HBox([Button_Count, Button_SelectAll, Button_SelectNone,
                          Button_MakeSelection, Button_PreviewQuestions, Button_ClearOutput]))
    display(tab)

    display(out)
    display(Button_ClearOutput)

    if isinstance(L[0], Question_MCQ):
    # if L[0].question_type == 'MCQ': # use Question Preview mode for MCQs
    # if L[0].__class__.__bases__[0] is Question_MCQ:       # use Question Preview mode for MCQs
        Selector_MasterMode.value='Question Preview'
        Selector_MasterMode.options=['Question Preview', 'Question & Answers']
        Button_SaveMarkingScheme.disabled=True
        Button_PrintMarkingScheme.disabled=True
        for i in range(len(L)):
                master.children[i].children[1].value=L[i].q_text()

# print("The following html code turns on MathJax:")
# print()
# print()
# print(r"""
# <script type="text/javascript" async="" src="https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.5/MathJax.js?config=TeX-MML-AM_CHTML"></script>
# </div>
# """
print("Imported the following functions:")
print("  nicify")
print("  nicify0")
print("  plus")
print("  pplus")
print("  suppress1")
print("  Taylor")
print("  scramble")
print("  scramble_full")
print("  tootrivial")
print("  latexdet")
print("  SaveToBBfile")
print("  PrintMarkingScheme")
print("  TypesetMarkingScheme")
print("  SaveMarkingScheme")
print()
print("Imported the following classes:") 
print("  MATHJAX")   
print("  linear_system")
print("  Question_written")
print("  Question_MCQ")      

import itertools, functools
import random as py_random
import re
      
      
def nicify(s):
    '''Performs some simplification of LaTeX code in s, only suitable in some cases.'''
    s = s.replace(r"\left(","(")
    s = s.replace(r"\right)",")")
    s = s.replace("y(x)","y")
    s = s.replace("log","ln")
    return(s)

      
def nicify0(s):
    '''Replaces "log" by "ln" and "y(x)" by "y" for DE-type questions.'''
    s = s.replace(r"y\left(x\right)","y")
    s = s.replace("log","ln")
    return(s)

def plus(x):
    '''Returns the LaTeX string "+x", where x is a number, unless x = 1 (resp. -1), 
    in which case it returns "+" (resp. "-").
    This is useful when x is meant to be a coefficient of something
    '''
    if x == 1: 
        return("+")
    if x == -1:
        return("-")
    if x >= 0:
        return("+"+latex(x))
    else:
        return("-"+latex(-x))

def pplus(x):
    '''Returns the LaTeX string "+x", unless x is negative, in which case it returns "-|x|".'''
    if x < 0:
        return("-"+latex(-x))
    else:
        return("+"+latex(x))
    
    

def suppress1(x):
    '''Returns the LaTeX string "x", where x is a number, unless x = 1 (resp. -1),
    in which case it returns "+" (resp. "-").
    This is useful when x is a coefficient of something.
    '''
    if x == 1:
        return("")
    if x == -1:
        return("-")
    else:
        return(latex(x))

def Taylor(f, a=0, n=10):
    '''Returns a latex string for the degree n Taylor polynomial of f about x=a.'''
    # produces the degree n Taylor polynomial of f about x=a, returns it as a latex string
    # SAGE's built-in Taylor expansion is often simplified in annoying ways
    x=var('x')
    s=''
    if a==0:
        for i in range(n+1):
            c = diff(f,x,i)(a)/factorial(i)
            sc = re.sub('x','',latex(c*x))  # encapsulate c in brackets if necessary
            if c!=0:
                if i==0:
                    if c==1:
                        s=latex(1)
                    elif c==-1:
                        s=latex(-1)
                    else:
                        s=sc
                elif i==1:
                    if c==1:
                        if len(s)>0:
                            s=s+'+'
                        s=s+'x'
                    elif c==-1:
                        s=s+'-x'
                    elif c<0:
                        s=s+sc+'x'
                    else:
                        if len(s)>0:
                            s=s+'+'
                        s=s+sc+'x'
                else:
                    if c==1:
                        if len(s)>0:
                            s=s+'+'
                        s=s+'x^{'+latex(i)+'}'
                    elif c==-1:
                        s=s+'-x^{'+latex(i)+'}'
                    else:
                        if (len(s)>0) & (sc[0]!='-'):
                            s=s+'+'
                        s=s+sc+'x^{'+latex(i)+'}'
    elif a>0:
        for i in range(n+1):
            c = diff(f,x,i)(a)/factorial(i)
            sc = re.sub('x','',latex(c*x))  # encapsulate c in brackets if necessary
            if c!=0:
                if i==0:
                    if c==1:
                        s=latex(1)
                    elif c==-1:
                        s=latex(-1)
                    else:
                        s=sc
                elif i==1:
                    if c==1:
                        if len(s)>0:
                            s=s+'+'
                        s=s+'(x-'+latex(a)+')'
                    elif c==-1:
                        s=s+'-(x-'+latex(a)+')'
                    else:
                        if (len(s)>0) & (sc[0]!='-'):
                            s=s+'+'
                        s=s+sc+'(x-'+latex(a)+')'
                else:
                    if c==1:
                        if len(s)>0:
                            s=s+'+'
                        s=s+'(x-'+latex(a)+')^{'+latex(i)+'}'
                    elif c==-1:
                        s=s+'-(x-'+latex(a)+')^{'+latex(i)+'}'
                    else:
                        if (len(s)>0) & (sc[0]!='-'):
                            s=s+'+'
                        s=s+sc+'(x-'+latex(a)+')^{'+latex(i)+'}'
    else: # a<0
        for i in range(n+1):
            c = diff(f,x,i)(a)/factorial(i)
            sc = re.sub('x','',latex(c*x))  # encapsulate c in brackets if necessary
            if c!=0:
                if i==0:
                    if c==1:
                        s=latex(1)
                    elif c==-1:
                        s=latex(-1)
                    else:
                        s=sc
                elif i==1:
                    if c==1:
                        if len(s)>0:
                            s=s+'+'
                        s=s+'(x+'+latex(-a)+')'
                    elif c==-1:
                        s=s+'-(x+'+latex(-a)+')'
                    else:
                        if (len(s)>0) & (sc[0]!='-'):
                            s=s+'+'
                        s=s+sc+'(x+'+latex(-a)+')'
                else:
                    if c==1:
                        if len(s)>0:
                            s=s+'+'
                        s=s+'(x+'+latex(-a)+')^{'+latex(i)+'}'
                    elif c==-1:
                        s=s+'-(x+'+latex(-a)+')^{'+latex(i)+'}'
                    else:
                        if (len(s)>0) & (sc[0]!='-'):
                            s=s+'+'
                        s=s+sc+'(x+'+latex(-a)+')^{'+latex(i)+'}'
    return(s)
      
      
def scramble(A,c=3):
    """Returns the matrix A with some random row operations performed on it."""
    rows=A.dimensions()[0]
    for i in range(rows):
        for j in range(i):
            A.add_multiple_of_row(i,j,randint(-c,c))
    return(A)

def scramble_full(A,c=3):
    """Returns the matrix A with some more random row operations performed on it."""
    rows=A.dimensions()[0]
    for i in range(rows):
        for j in range(rows):
            if i!=j:
                A.add_multiple_of_row(i,j,randint(-c,c))
    return(A)

def tootrivial(A):
    """Returns true if A has two equal rows, a row equal to -(another row) or a row of zeroes."""
    [rows,cols]=A.dimensions()
    zero=[0 for i in range(cols)]
    for i in range(rows):
        if list(A.row(i))==zero:
            #print("Row %s is zero"%str(i))
            return true
        for j in range(i):
            if (A.row(i)==A.row(j))|(A.row(i)==-1*A.row(j)):
                #print("Rows %s and %s are equal"%(i,j))
                return true
    return false

def latexdet(A):
    """Returns a LaTeX string for the determinant of A using vertical bars."""
    s=latex(A).replace("\\left(","\\left|")
    s=s.replace("\\right)","\\right|")
    return(s)
      
      
class MATHJAX():
    '''Takes an HTML formatted string with embedded LaTeX and typesets it. By Bjoern Rueffer'''
    def __init__(self,s):
        self.s = s
    def _repr_html_(self):
        '''this is used by display() / show() in your jupyter notebook'''
        return '''
        <div>
        <script type="text/javascript" async="" src="https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.5/MathJax.js?config=TeX-MML-AM_CHTML"></script>
        </div>''' + self.s
    def __str__(self):
        '''this is used by print() and str()'''
        return(self._repr_html_())
      

        
class linear_system(object):
    """This class defines a system of linear equations by its r x (c+1) augmented matrix.
    
    The methods allow us to nicely typeset the equations and the augmented matrix.
    
    To Do:
        - Typeset equations nicely in an array with variables lined up
         """
    def __init__(self,C,varnames):
        """C is an r x (c+1) matrix; varnames is a list of c names for the variables"""
        self.C = C
        self.r = C.dimensions()[0]
        self.c = C.dimensions()[1]-1
        if len(varnames) != self.c:
            raise ValueError("Expected %s variables, but received %s"%(str(self.c),str(len(varnames))))
        self.X = var(varnames) # this is now a list of c variables
        self.eqs = []  # next, we create a system of symbolic equations
        for i in range(self.r):
            lhs = 0 
            for j in range(self.c):
                lhs = lhs + self.C[i,j]*self.X[j]
            self.eqs.append(lhs == self.C[i,self.c])
        #self.sol = solve(self.eqs,self.X,solution_dict=true)
        self.A = self.C.matrix_from_columns(range(self.c))  # coefficient matrix
        self.b = self.C.matrix_from_columns([self.c])  # last column = RHS of equations, so system is Ax=b
        self.V = self.A.right_kernel_matrix().rows() # basis of free part of solution
        
        
        
    def __repr__(self):
        return "Linear system defined by \n"+str(self.C)
    
    def latex_eqs(self):
        """Return LaTeX code for the system of equations, using \\align.
        In future, I'd like to implement nicer typesetting in an array."""
        return("\\begin{align*}\n"\
               +"\\\\ \n".join([latex(eq.left_hand_side())+"&="+latex(eq.right_hand_side()) for eq in self.eqs])+\
              "\n\\end{align*}")
    
    def latex_augmented_matrix(self):
        """Return LaTeX code for the agumented array."""
        return("\\left[\\begin{array}{"+"".join(["r" for i in range(self.c)])+"|r}\n"+\
               "\\\\ \n".join([" & ".join([latex(self.C[i,j]) for j in range(self.c+1)]) for i in range(self.r)])+\
               "\n\\end{array}\\right]"
              ) 
    
    def latex_sol(self):
        """Return LaTeX code for solution set of system"""
        self.num_parameters = len(self.V) # number of free parameters in solution
        if self.num_parameters <= 1:
            self.T = var(["t"])  # name of one free parameter
        else:
            self.T = var(["t"+str(i+1) for i in range(self.num_parameters)]) # names for free parameters
        try:
            self.v0 = vector(self.A.solve_right(self.b)) # a particular solution - if it exists
        except:
            self.v0 = none 
            return("\\{\\}")   # no solutions
        s = "\\{"+latex(self.v0)
        if self.num_parameters > 0:
            s = s+"+"+" + ".join([latex(self.T[i])+latex(self.V[i]) for i in range(self.num_parameters)])
            s = s+", \\;"+", ".join([latex(self.T[i]) for i in range(self.num_parameters)])+" \\in \\mathbb{R}"
        s = s+"\\}"
        return(s)      
      
class Question_Written(object):
    '''This is a written question. 
    
    The most important attributes are the two strings:
      self.question_text   which contains the question
      self.solution_text   which contains the full solution
    
    It also contains summary data about the question to be included as a row in a LaTeX table of questions:
      self.table_header contains the headings for a table of question variants (e.g. question, answer).
      self.table_row contains the entries of a row containing this info.
    
    Various methods display this data, save the marking scheme to a .tex file, etc.
    '''
    
    def __init__(self):
        self.points = 0
        self.variant_number = 0
        self.question_text = "there is no question text yet"
        self.solution_text = "no solution to no question"
        self.rubric = r"""
\noindent{\bf Marking Scheme:}
\begin{small}
\begin{itemize}
  \item 1 mark: The student demonstrates a partial understanding of how to do the problem.
  \item 2 marks: The student demonstrates a good understanding of how to do the problem \\ (some minor errors permitted).
  \item 3 marks: The student demonstrates a good understanding and obtains the correct answer.
\end{itemize}
\end{small}"""
        self.table_row = []
        self.table_header = []
        
        
#     def __repr__(self):
#         return "An unspecified written-answer question worth %s points"%self.points

    def make_BB_row(self): 
        '''Returns a row for writing self to a Blackboard file.
        This code owes much to Bjoern Rueffer.'''
        self.BB_question_text = self.question_text
        self.BB_question_text = re.sub(r'\$\$(.*?)\$\$',r'\\[\1\\]',self.BB_question_text)
        self.BB_question_text = re.sub(r'\$(.*?)\$',r'\\(\1\\)',self.BB_question_text)
        self.BB_question_text = re.sub(r'\\dfrac\b',r'\\frac',self.BB_question_text)
        self.BB_question_text = re.sub('[\n ]+',' ',self.BB_question_text)
        return("FIL\t"+self.BB_question_text+"\n")

    
    def write_BB_row(self, f):  #f is a file that's already been opened for writing
        '''Writes the question in one line to file f (assumed to be open and writable) in the correct format for BlackBoard.
        This code owes much to Bjoern Rueffer.'''
        f.write(self.make_BB_row())
        
    
    def __repr__(self):
        return(self.question_text)
    
    def latex_question_text(self):
        '''Returns self.question_text with "<br>" replaced by "\n\n".'''
        return(self.question_text.replace("<br>","\n\n"))
    
    def latex_solution_page(self,var_number=-1):
        '''Returns a page for the marking scheme; var_number is an optional variant number '''
        if var_number==-1:
            var_number=self.variant_number  # i can be changed post-hoc in case variant_number wasn't initially supplied
        s = "\\newpage\n\\section{Variant "+str(var_number)+"}\n\\label{v"+str(var_number)+"}\n\n"+\
        self.latex_question_text()+"\n\\medskip\n\n"+r"\noindent{\bf Solution.}"+"\n\n"+self.solution_text+"\n\\medskip\n\n"+self.rubric
        return(s)
    
    def test_solution_page(self,filename="test.tex",var_number=-1):
        '''Writes the solution page to a ready-to-compile LaTex file for testing'''
        with open(filename,'w') as f:
            f.write(r"\documentclass{article}"+"\n"+r"\usepackage{amssymb,amsmath,hyperref,a4wide}"+"\n\n"+r"\begin{document}"+"\n"+\
            self.latex_solution_page(var_number=var_number)+"\n"+r"\end{document}") 
    
    def _repr_html_(self):
        return(self.question_text)
      

class Question_MCQ(object):
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
        
        
    """
    def __init__(self):
        self.points = 0
        self.answer = ""
        self.wrong_answers = []
        self.question_text = "An empty question"
        self.answer_shuffle = [0,1,2,3]
        self.answer_index = 0
        self.shuffle_seed = randint(1,10000)
    
   
    def __repr__(self):
        return(self.question_text)
    
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
        py_random.shuffle(answers)
        answers = itertools.chain(*answers)
        answers = list(answers)
        return ('MC',question, *answers, 'None of the others', 'incorrect')
    
    def write_BB_row(self, f):  #f is a file that's already been opened for writing
        '''Writes the question in one line to file f (assumed to be open and writable) in the correct format for BlackBoard'''
        f.write("\t".join(self.make_BB_row())+"\n")
    
    def latex_sorted(self):
        '''Returns LaTex code that typsets the question and answers. Correct answer listed first.'''
        return self.question_text+"\n\\begin{enumerate}\n  \\item %s \n  \\item %s \n"%(self.answer,self.wrong_answers[0])+\
    "  \\item %s \n  \\item %s \n  \\item None of the others \n\\end{enumerate}"%(self.wrong_answers[1], self.wrong_answers[2])
    
    def shuffle(self, s=0):
        '''Shuffles the four answers, using the random seed self.shuffle_seed, which can be set by the optional parameter s.'''
        if s!=0:
            self.shuffle_seed = s
        self.answer_shuffle = [0,1,2,3]
        with seed(self.shuffle_seed):
            shuffle(self.answer_shuffle)
        i=1
        for a in self.answer_shuffle:
            if a==0: self.answer_index = i
            i+=1
            
    def latex_shuffled(self):
        '''Returns LaTex code that typsets the question and answers. 
        Answers are listed in the order determined by self.answer_shuffle'''
        answers = [self.answer]+self.wrong_answers
        answers = [answers[x] for x in self.answer_shuffle]
        return self.question_text+"\n\\begin{enumerate}\n  \\item %s \n  \\item %s \n"%(answers[0],answers[1])+\
    "  \\item %s \n  \\item %s \n  \\item None of the others \n\\end{enumerate}"%(answers[2], answers[3])
    
    def has_distinct_answers(self):
        '''Returns true if all answers are distinct.'''
        answers = [self.answer]+self.wrong_answers
        return len(answers)==len(set(answers))
    
    def _repr_html_(self):
        s=self.question_text+r"<br><ol>"+\
        "\n".join([r"<li>"+a+r"</li>" for a in [self.answer]+self.wrong_answers+["None of these"]])+\
        r"</ol>"
        return(s)    
      
def SaveToBBfile(L, filename):
    '''Saves a list L of questions to a file for uploading to Blackboard.''' 
    with open(filename,'w') as f:
        for Q in L:
            Q.write_BB_row(f)
      
      
def PrintMarkingScheme(L, course="MATH1120 2020 S2 ", title="", print_table=true, array_stretch=1):
    '''Prints a marking scheme for the list L of written-answer questions'''
    print(r"\documentclass{article}")
    print(r"\usepackage{amssymb,amsmath,hyperref,a4wide}")
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
    
    
def TypesetMarkingScheme(L, course="MATH1120 2020 S2 ", title="", print_table=true, array_stretch=1):
    '''Returns a marking scheme for the list L of written-answer questions'''
    s=r"\documentclass{article}"+"\n"+\
    r"\usepackage{amssymb,amsmath,hyperref,a4wide}"+"\n\n"+\
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
        s+=r"\medskip"+"\n"+\
        r"\begin{tabular}{|l|"+"".join(["l|" for i in range(cols)])+"}"+\
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
        s+=r"\end{tabular}"+"\n\n"
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


def SaveMarkingScheme(L, filename, course="MATH1120 2020 S2 ", title="", print_table=true, array_stretch=1):
    '''Writes the marking scheme for the list L of questions to filename.'''
    with open(filename,'w') as f:
        f.write(TypesetMarkingScheme(L,course=course,title=title,print_table=print_table,array_stretch=array_stretch))
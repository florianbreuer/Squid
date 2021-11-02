from sage.misc.latex import latex

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

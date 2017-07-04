from sys import argv
from subprocess import call
import os.path
from datetime import datetime

def get_subdir(subdir):
    try:
        os.mkdir(subdir)
    except Exception:
        pass
    return subdir

def write_to_file(subdir, name, data):
    get_subdir(subdir)
    f = open(os.path.join(subdir, name), 'w')
    f.write(data)
    f.close()
    
def get_vertices(first, second):
    hdiff = second[0] - first[0]
    vdiff = second[1] - first[1]
    third = [0, 0]
    fourth = [0, 0]
    third[1] = second[1] + hdiff
    third[0] = second[0] - vdiff
    fourth[0] = third[0] - hdiff
    fourth[1] = third[1] - vdiff
    return [first, second, third, fourth]
    
def get_inner(first, second, a, b):
    hdiff = second[0] - first[0]
    vdiff = second[1] - first[1]
    inner = [0, 0]
    inner[0] = first[0] + (hdiff * a / (a + b))
    inner[1] = first[1] + (vdiff * a / (a + b))
    return inner
    
def get_inner_vertices(first, second, a, b):
    vertices = get_vertices(first, second)
    inner_first = get_inner(first, second, a, b)
    inner_second = get_inner(second, vertices[2], a, b)
    return get_vertices(inner_first, inner_second)
    
def get_nested_squares(first, second, a, b, num_sq):
    if num_sq < 1:
        return []
    outside = get_vertices(first, second)
    squares = [outside]
    for _ in range(num_sq - 1):
        outside = squares[-1]
        squares.append(get_inner_vertices(outside[0], outside[1], a, b))
    return squares

def get_formatted_nested_squares(first, second, a, b, num_sq, places = 3):
    format_str = "%." + str(places) + "f"
    formatted_squares = []
    squares = get_nested_squares(first, second, a, b, num_sq)
    for sq in squares:
        sq_formatted = []
        for pt in sq:
            pt_formatted = [format_str % coord for coord in pt]
            sq_formatted.append(pt_formatted)
        formatted_squares.append(sq_formatted)
    return formatted_squares

def print_nested_squares(first, second, a, b, num_sq, places = 3):
    squares = get_formatted_nested_squares(first, second, a, b, num_sq, places)
    for sq in squares:
        print(sq)
       
def sqbr(color):
    return "[" + color + "] "

def make_tikz_str(square, color):
    tikz_str = "\t\\draw " + sqbr(color)
    for pt in square:
        tikz_str += "(" + str(pt[0]) + ", " + str(pt[1]) + ") -- "
    tikz_str += "cycle;"
    return tikz_str
    
def brace(p, q, r):
    return p + "{" + q + "}" + r
    
def make_tikzpicture_str(first, second, a, b, num_sq, color = "black", places = 3):
    squares = get_formatted_nested_squares(first, second, a, b, num_sq, places)
    tikz_str = brace("\\begin", "tikzpicture", "\n")
    for sq in squares:
        tikz_str += make_tikz_str(sq, color) + "\n"
    tikz_str += brace("\\end", "tikzpicture", "\n")
    return tikz_str
    
def make_tex_str(scale, a, b, num_sq, color = "black", places = 3):
    first = [scale, scale]
    second = [-scale, scale]
    page_size = scale * 4/5
    pic_size = scale * 4/5
    side_margin = -1
    top_margin = -7/8 * ((127 + scale)/(61 + scale))
    data = brace("\\documentclass", "letter", "\n")
    data += brace("\\usepackage", "tikz", "\n\n")
    data += "\\pdfpagewidth " + str(page_size) + "in\n"
    data += "\\pdfpageheight " + str(page_size) + "in\n"
    data += brace("\\setlength", "\\oddsidemargin", "") + brace("", str(side_margin) + "in", "\n")
    data += brace("\\setlength", "\\evensidemargin", "") + brace("", str(side_margin) + "in", "\n")
    data += brace("\\setlength", "\\topmargin", "") + brace("", str(top_margin) + "in", "\n")
    data += brace("\\setlength", "\\textwidth", "") + brace("", str(pic_size) + "in", "\n")
    data += brace("\\setlength", "\\textheight", "") + brace("", str(pic_size) + "in", "\n")
    data += brace("\\pagestyle", "empty", "\n")
    data += brace("\n\\begin", "document", "\n\n")
    data += brace("\\begin", "center", "\n")
    data += make_tikzpicture_str(first, second, a, b, num_sq, color, places)
    data += brace("\\end", "center", "\n")
    data += brace("\n\\end", "document", "")
    return data 

def make_tex_file(subdir, name, scale, a, b, num_sq = 4, color = "black", places = 3):    
    data = make_tex_str(scale, a, b, num_sq, color, places)
    if name.find(".tex") == -1:
        name += ".tex"
    write_to_file(subdir, name, data)
    return name
    
def mv_files(sub, basename, exts):
    for ext in exts:
        name = basename + "." + ext
        call(["mv", name, os.path.join(sub, name)])
        
def make_pdf(sub, basename, name):
    call(["pdflatex", os.path.join(sub, name)])
    mv_files(sub, basename, ["pdf", "log", "aux"])
    return basename + ".pdf"
    
def make_svg(sub, pdfname, abbrev):
    svgsub = "SVG"
    get_subdir(svgsub)
    call(["pdf2svg", os.path.join(sub, pdfname), os.path.join(svgsub, abbrev + ".svg")])
    return abbrev + ".svg"
    
def pdf_nested_squares(leg_a="5", leg_b="12", num="4", scale="4.913", namestub="pythagorean-rose", sub="nested-pythagorean", color="black", prec="4"):
    legs = leg_a + "+" + leg_b
    suffix = "-legs" + legs + "-nested" + num + "-scale" + scale + "-" + color
    basename = namestub + suffix
    name = make_tex_file(sub, basename, float(scale), int(leg_a), int(leg_b), int(num), color, int(prec))
    make_pdf(sub, basename, name)
    
def get_hex(n):
    hx = ""
    while n > 0:
        r = n % 16
        n = int((n - r)/16)
        if r < 10:
            hx = str(r) + hx
        else:
            hx = chr(ord('A') + r - 10) + hx
    return hx
    
def make_hex_time():
    time = datetime.now().strftime('%y%m%d-%H%M%S')
    a = int(time[:6])
    b = int(time[7:])
    time = get_hex(a) + get_hex(b)
    return time
   
def nest_squares(a, b, n, s, color="black", p = 4):
    namestub = "pythagorean-rose"
    legs = str(a) + "+" + str(b)  
    suffix = "-legs" + legs + "-nested" + str(n) + "-scale" + str(s) + "-" + color
    basename = namestub + suffix
    abbrev = "pythrose" + legs + "-n" + str(n) + "-s" + str(s) + "-" + color
    sub = "nestedpyth-" + legs + "-n" + str(n) + "-" + make_hex_time()
    name = make_tex_file(sub, basename, s, a, b, n, color, p)
    pdfname = make_pdf(sub, basename, name)
    svgname = make_svg(sub, pdfname, abbrev)
    
def parse_nest_to_pdf(argv):
     # set defaults
        
        leg_a = "3"
        leg_b = "4"
        num = "5"
        scale = "5"
        namestub = "pythagorean-rose"
        sub = "nestedpyth-" + make_hex_time()
        color = "black"
        prec = "4"
        
        if len(argv) > 1:
            leg_a = argv[1]
        if len(argv) > 2:
            leg_b = argv[2]
        if len(argv) > 3:
            num = argv[3]
        if len(argv) > 4:
            scale = argv[4]
        if len(argv) > 5:
            namestub = argv[5]
        if len(argv) > 6:
            sub = argv[6]
        if len(argv) > 7:
            color = argv[7]
        if len(argv) > 8:
            prec = argv[8]

        pdf_nested_squares(leg_a, leg_b, num, scale, namestub, sub, color, prec)

if __name__ == '__main__':
    parse_nest_to_pdf(argv)
   

## Generating output from rules
from checker import Rule, RuleType, DesignDict
from intermediate import ViolationSummary
import subprocess
import os
import re
import logging
from datetime import date
import time
from config import *

logger = logging.getLogger('root')
pdflatex = "/usr/bin/pdflatex"

def mangleFile(path):
    """
    Given the dxf file name (path), produce the appropriate pdf and tex output
    locations.
    """
    baseName = os.path.basename(path)
    dirName = os.path.dirname(path)
    noExt = os.path.splitext(baseName)[0]
    asTex = noExt + ".tex"
    asPDF = noExt + ".pdf"
    asDXF = noExt + ".dxf"
    return (asTex, asPDF, asDXF)

def sectionString(sname):
    """
    Add a given section to the tex
    """
    return "\\sect{%s}" % sname

def subSectionString(sname):
    """
    Add a given subsection to the tex
    """
    return "\\subsect{%s}" % sname

def ruleVString(sname):
    """
    Add a rule section to the tex (sembler specific)
    """
    return "\\rulesect{%s}" % sname

def purityVString(sname):
    """
    Add a purity vilotaion section to the tex
    """
    return "\\puritysect{%s}" % sname

def suggString(sname):
    """
    Add a suggestion violation section to the tex (sembler specific)
    """
    return "\\suggsect{%s}" % sname

def addImage(path):
    """
    Add an image (probably a checkplot) to the tex
    """
    return "\\addpage{%s}\n" % path

def checkplotString(paths):
    """
    Adds labeled subsections containing a checkplot.  Label reflects the layer
    in the checkplot.

    Assumes an order over the checkplots to be added.
    """
    outputString = ""
    labels = ["L3\_SU8","L2\_SU8", "L1\_SU8", "METAL", "Port Alignment"]
    if paths:
        outputString = checkplotBP
        for path in paths:
            heading = labels.pop()
            outputString = "%s\n\\newpage" % outputString
            outputString = "%s\n\\begin{figure}[h!]\n\\begin{center}\n" % outputString
            outputString = "%s\n%s" % (outputString, addImage(path))
            outputString = "%s\n\\end{center}\\caption{%s Layer}\n" % (outputString, heading)
            outputString = "%s\n\\end{figure}\n" % outputString
            if heading is "Port Alignment":
                outputString = "%s\n%s" % (outputString, alignmentText)
    outputString = "%s\n\\newpage" % outputString
    return outputString


def violationDescString(violation):
    """
    Adds a section showing a violation of a rule or suggestion. Takes an actual
    rule as input, and determines if a rule or suggestion was violated based on
    that rule.
    """
    ## Set up the subsection header w/ appropriate color
    if violation.ctype == RuleType.HARD:
        base = ruleVString(violation.name)
    elif violation.ctype == RuleType.SOFT:
        base = suggString(violation.name)
    elif violation.ctype == RuleType.PURITY:
        base = purityVString(violation.name)
    ## flesh out the rest of the string and return
    return "%s\nOn Layer %s\n\n\t%s" % (base, re.sub("_", "\_", violation.dxfLayer), violation.desc)

def countString(i):
    """
    Text for saying how many times a given rule / suggestion was violated by a
    design.
    """
    return "\t\tWe found %d violations of this kind." % i

def violationString(violation, vcount):
    """
    Produces an entire rule section, including the rule's subheader, the long
    description of that rule, and text stating how many times the rule was
    violated.
    """
    return "%s\n\n%s" % (violationDescString(violation), countString(vcount))


def generateViolatedRuleOutput(vSummary):
    """
    Builds a summary table of rules / suggestions violated by layer.
    """

    outputString = sectionString("Table of Issues")
    ## Output Summary Table

    outputString = "%s\n\n%s" % (outputString, vSummary.tex())

    ## Output information layer by layer, rule by rule
    for (layer, violations) in vSummary.violationsByLayer.items():
        lname = layerNumToName(layer)
        if len(violations) > 0:
            outputString = "%s\n\n%s" % (outputString, sectionString("Issues in %s" % lname))

        for (rid,vl) in violations.items():
            if vl:
                exemplar = vl[0]
                outputString = "%s\n\n%s" % (outputString, violationString(exemplar, len(vl)))
            else:
                logger.error("Ended up with an empty violation group in a layer. Something broke in ViolationSummary")

    return outputString

def statusString(vSummary):
    if vSummary.sawPurity:
        return unreadable
    elif vSummary.sawHard:
        return fail
    elif vSummary.sawSoft:
        return warn
    else:
        return passed

def generateExplanatoryBP(inputDxf, status):
    d = date.fromtimestamp(time.time())
    timeString = d.isoformat()
    return standardBP % (re.sub("_", "\_", inputDxf), status, timeString, version)

def generateOutputBP(asDXF, asPDF, outDXF, vSummary):
    cleanDXF = re.sub("_", "\_", asDXF)
    errDXF = re.sub("\.dxf", "-err.dxf", cleanDXF)
    base = outputBP % (re.sub("_", "\_", asPDF), cleanDXF, errDXF)
    if vSummary.sawPurity or vSummary.sawHard or vSummary.sawSoft:
        return base
    else:
        return "%s\n%s" % (base, noErrorsErrDXF)

def generateFailureType(vSummary):
    if vSummary.sawPurity:           ## Couldn't ingest
        return impureBP
    elif vSummary.sawHard:           ## Hard failures, can't manufacture
        return hardBP
    elif vSummary.sawSoft:           ## Soft failures, might not come out right
        return softBP
    else:                            ## all is well and right with the dxf
        return successBP

def outputPDF(violationSummary, checkplotPaths, dxfPath, outDir, vstring):
    """
    Produces a summary pdf of the drc's evaluation of a given design dictionary.
    Takes a variety of input, including violations found by the DRC
    (purityViolations, violationList), paths to checkplots of the design
    (checkplotPaths), the path to the input dxf file (dxfPath) and an output
    directory to drop the pdf into (outdir).
    """
    if os.path.exists(pdflatex):
        (asTex, asPDF, asDXF) = mangleFile(dxfPath)

        subprocess.call(["cp", req_root + "/cover.pdf", outDir])

        purity = violationSummary.sawPurity
        hard = violationSummary.sawHard
        soft = violationSummary.sawSoft

        ##Setup front of document
        outputString = preamble
        outputString = "%s\n%s" % (outputString, addImage("cover.pdf"))
        outputString = "%s\n%s" % (outputString, "\\newpage")

        ## Add general 'What is this document' boiler plate
        outputString = "%s\n%s" % (outputString, generateExplanatoryBP(asDXF, statusString(violationSummary)))

        ## I need to know what the output dxf is here.  When do I know this? [JTT 15-03-16]
        outputString = "%s\n%s" % (outputString, generateOutputBP(asDXF, asPDF, asDXF, violationSummary))

        ## Add general run result boiler plate
        outputString = "%s\n%s" % (outputString, generateFailureType(violationSummary))

        ## Beyond here is where we really have to do the real refactoring
        ## Print detailed rule information
        outputString = "%s\n%s" % (outputString, generateViolatedRuleOutput(violationSummary))

        ## If applicable, render checkplots
        outputString = "%s\n%s" % (outputString, checkplotString(checkplotPaths))

        ## Tag with a sembler version number and close
        outputString = "%s\n\n%s" % (outputString, end)

        ## String is built -- emit the .tex and compile it
        startDir = os.getcwd()
        os.chdir(outDir)
        open(asTex, "wb").write(outputString)
        subprocess.call(["pdflatex", "-interaction=batchmode", asTex])
        os.chdir(startDir)
        return asPDF
    else:
        logger.error("pdflatex not in path. Can't compile tex.")
        return ""

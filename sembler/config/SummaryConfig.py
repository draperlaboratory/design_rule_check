import os
req_root = os.getenv('SEMBLER_TEMPLATES', '.')

## Tex specific, probably don't want to touch any of this
opening = "\\documentclass[twoside]{article}\n"
semblersty = "\\input{" + req_root + "/sembler.sty}\n"
preamble = opening + semblersty + "\n\\begin{document}\n" + "\\title{Sembler DRC Report Content}"
end = "\\end{document}"


unreadable = "UNREADABLE"
fail = "FAILED"
warn = "PASSED WITH CONDITIONS"
passed = "PASSED"

## These string are inserted verbatim into the tex document that makes up the summary.
## Remember to escape strings as if you're writing tex!
## Needs 4 Arguments -- DXF file name, Status, Time String, and Version Number String
standardBP = """
\\sect{Summary}
\\begin{tabular}{lr}
Design file:& $<$%s$>$\\\\
Design status:& %s\\\\
Design rule check performed on:& %s\\\\
Design Rule Checker (DRC) version:& $<$%s$>$\\\\
\\end{tabular}
"""

## Needs 3 Arguments, Input DXF FileName, Output PDF FileName, Output DXF FileName
outputBP = """
\sect{Output}
The DRC generated a ZIP file with feedback on your design. This ZIP file contains:
\\begin{itemize}
\\item \\texttt{$<$%s$>$}: this report
\\item \\texttt{$<$%s$>$}: your submitted design file
\\item \\texttt{$<$%s$>$}: an ``output DXF'' file that contains your design with notation from the DRC
\\end{itemize}
This report guides you in interpreting the DRC feedback.
"""
noErrorsErrDXF = """
Please note: the DRC has generated an ``output DXF'' file for your submission, but
since we found no errors or warnings in your design, you can disregard this file.
"""

## No Arguments, boilerplate for unreadable instances
impureBP = """
\\sect{Design status}
\\subsect{UNREADABLE}

The Design Rule Checker could not read your design file. This occurs when your
design contains one of the following:

\\begin{itemize}
\\item Open polylines
\\item Self-intersecting features
\\item Invalid entities such as splines
\\end{itemize}

For more information, review the reported issues in this document, as well as
the output DXF. When you have fixed these issues, resubmit your updated
design. If you require assistance, contact
\\href{mailto:sembler@draper.com}{sembler@draper.com}.

"""

## No arguments. Boilerplate for instances with only warnings.
softBP = """
\\sect{Design status}
\\subsect{PASSED WITH CONDITIONS}

Your design has features that exceed one or more of the Design Guidelines (see
\\href{https://sembler.draper.com/files/sembler_process_rules.pdf}{Sembler Design
Rules and Process Description (PDF)}). Sembler can fabricate your device, but
you assume some additional risk that the device might not function as you
intend. To mitigate this risk, edit and resubmit your design until it passes the
Design Rule Check with fewer or no conditions.

For more information, review the reported warnings and the checkplots in this
document, as well as the output DXF file. If you require assistance, contact
\\href{mailto:sembler@draper.com}{sembler@draper.com}.

\subsect{DXF Witness Markings}

\\begin{description}
\item[Point] Points are highlights in the annotated DXF that are meant to show
single poinst in the submitted design that somehow conflict with the rules or
guidelines.  For example, we will highlight the point at which two lines cross
one another instead of forming a continuous geometric shape (also known as a
self-intersecting error).

\item[Circle] This is a highlight that is added in the annotated DXF file to
direct you to an area of a feature that somehow conflicts with the design rules
or guidelines.  For example, if a feature in your final PDMS is designed to be
so large that it is in danger of collapse, we will draw a circle inscribed in
the too-large region to draw it to your attention.  Another example of when you
might see a circular highilight is in the case when a port in your design is not
one of the stated sizes; here, we would highlight the entire port using a
circle.

\item[Line Segment] This inserts a highlighted line between two points
in the annotated DXF file, and is primarily used for showing pitch issues
between objects that are either too near together or too far apart.  For
example, a line is drawn between two feature that are too close to one another
and that will create a risk of fluid leakage.  In the case of spacing issues
involving ports and bondpads, we will draw the line segments from center to
centr, rather than edge to edge.

\item[Region] Region highlights in your annotated DXF are exclusively used for
unsupported geometry.  We will highlight the geometry that isn't supported by
the layer below to help you make sure that layers 2 and 3 of the SU-8 mold have
adequate support in the lower layer(s).

\end{description}
"""

## No arguments. Boilerplate for instances that violate rules
hardBP = """
\\sect{Design status}
\\subsect{FAILED}
Your design has features that violate one or more of the Design Rules (see
\\href{https://sembler.draper.com/files/sembler_process_rules.pdf}{Sembler Design
Rules and Process Description (PDF)}). In order for Sembler to fabricate your
design, it needs to pass the Design Rule Check with no rule violations.

For more information, review the reported errors and the checkplots in this
document, as well as the output DXF file. When you have fixed these errors,
resubmit your updated design. If you require assistance, contact
\\href{mailto:sembler@draper.com}{sembler@draper.com}.

\\begin{description}
\item[Point] Points are highlights in the annotated DXF that are meant to show
single poinst in the submitted design that somehow conflict with the rules or
guidelines.  For example, we will highlight the point at which two lines cross
one another instead of forming a continuous geometric shape (also known as a
self-intersecting error).

\item[Circle] This is a highlight that is added in the annotated DXF file to
direct you to an area of a feature that somehow conflicts with the design rules
or guidelines.  For example, if a feature in your final PDMS is designed to be
so large that it is in danger of collapse, we will draw a circle inscribed in
the too-large region to draw it to your attention.  Another example of when you
might see a circular highilight is in the case when a port in your design is not
one of the stated sizes; here, we would highlight the entire port using a
circle.

\item[Line Segment] This inserts a highlighted line between two points
in the annotated DXF file, and is primarily used for showing pitch issues
between objects that are either too near together or too far apart.  For
example, a line is drawn between two feature that are too close to one another
and that will create a risk of fluid leakage.  In the case of spacing issues
involving ports and bondpads, we will draw the line segments from center to
centr, rather than edge to edge.

\item[Region] Region highlights in your annotated DXF are exclusively used for
unsupported geometry.  We will highlight the geometry that isn't supported by
the layer below to help you make sure that layers 2 and 3 of the SU-8 mold have
adequate support in the lower layer(s).

\end{description}
"""

## No arguments, Boilerplate for instances with 0 issues
successBP = """
\sect{Design status}
\subsect{PASSED}
Success! Your design has passed the Design Rule Check with no rule violations and without exceeding any guidelines.
"""

checkplotBP = """
\\sect{Checkplots}
Review the checkplots for the SU-8 and metal layers to verify that the Design
Rule Checker correctly interprets your design.

\\par Fluidic and metal features appear in white, while substrate and bulk PDMS
appear in gray. For reference, ports and alignment marks are shown in each layer
as black dashed lines. Note also that the DRC automatically maps support posts
to the SU-8 layers where features exist.
"""

alignmentText ="""
The port alignment layer shows which portions of the
metal layer will be exposed by vertical ports.  The ports will not be
punched all the way through the metal layer. We render them as a visual
aid.
"""


## Not Rendered, Probably don't need to touch this.
notice = "%% Automatically Generated by Sembler Design Constraint Checker %%"

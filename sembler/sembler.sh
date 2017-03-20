#!/bin/bash

PYTHON=/usr/local/bin/python2.7
SEMBLER=$SEMBLER_PATH/sembler.py
DEFAULT_PDF=$SEMBLER_TEMPLATES/generic.pdf
DEFAULT_JSON=$SEMBLER_TEMPLATES/generic.json
JSON_SUFFIX=-result.json
PDF_SUFFIX=.pdf

legalDir()
{ # Is the argument both extant and a directory
    if [ -e $outdir ]
    then
        if [ -d $outdir ]
        then
            return 0
        else
            echo $outdir is not a directory
        fi
    else
        echo $outdir does not exist
    fi
    return 1
}

exitError()
{ # The bad exit.  Something is really hosed (I can't write to output) and we're bailing.
    echo "Sembler.sh is broken beyond repair. This will end badly."
    exit 1
}

exitFailure()
{ # The less bad exit. sembler.py died somehow, and we're throwing out the generic fail pdf
    echo "Sembler is broken in an anticipated way. This is bad, but not catastrophic."
    filename=$1
    cp $DEFAULT_PDF $outdir/$filename$PDF_SUFFIX
    cp $DEFAULT_JSON $outdir/$filename$JSON_SUFFIX
    exit 0
}

cleanOutput()
{ #Clean up after a successful sembler run.  This should be rolled into sembler.py someday
    rm -f $outdir/*.tex
    rm -f $outdir/*.aux
    rm -f $outdir/*.log
    rm -f $outdir/*_SU8_*.json
    rm -f $outdir/*_SU8_*.pdf
    rm -f $outdir/*_metal.json
    rm -f $outdir/*_metal.pdf
}

## Name each of the expected arguments
if [ $# -eq 3 ]
then
    fname=$1
    indir=$2
    outdir=$3
    pid="NaN"
elif [ $# -eq 4 ]
    fname=$1
    indir=$2
    outdir=$3
    pid=$4
else
    echo "Expected up to 4 parameters. DXF name, input directory, output directory, (pid)"
    exitError
fi

fnamenoext=$(basename "$fname" .dxf)

echo "running on $1 $2 $3"
## Is the input directory extant and a directory
legalDir $indir
if [ $? -ne 0 ]
then
    exitError
fi

echo $indir ok
## Is the output directory extant and a directory
legalDir $outdir
if [ $? -ne 0 ]
then
    exitError
fi

echo $outdir ok
## Run sembler on the input
$PYTHON $SEMBLER $fname $indir $outdir $pid

if [ $? -ne 0 ]
then # Did sembler choke on the input?
    exitFailure "$fnamenoext"
else # No? Good. Cleanup
    cleanOutput "$fnamenoext"
fi

## Successful run and clean exit
exit 0

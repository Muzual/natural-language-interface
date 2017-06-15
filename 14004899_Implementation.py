#
# Natural Language Interface to Databases
#       Written by Miles Schofield
#
# Written with PYTHON 3.6.0
# Requires NLTK (3.0 used) and cx_Oracle modules installed
# Operates with a local Oracle 11g Database
import time
import string
import nltk
import re
from nltk.corpus import stopwords
import cx_Oracle
#
# @AUTHOR Miles Schofield macschofield@blueyonder.co.uk
# @VERSION 6.1
#
#                   CONNECTION
# Code responsible for connecting to the Oracle db
#
# Username and password require changing per instance
# Cursor used for querying is defined as global
# Program exits if connection failed in order to prevent
# an infinite loop.
#
# @exception cx_Oracle.DatabaseError
# @throws exception Failed to Connect


def databaseConnection():
    username = 'SYSTEM'
    password = 'x'
    print("Database Connection:", sep="", end="", flush=True)
    try:
        connection = cx_Oracle.connect(username, password)
        global curs
        curs = connection.cursor()
        print(" SUCCESS!")
    except cx_Oracle.DatabaseError as exception:
        print("Failed to connect")
        time.sleep(2)
        exit()
    return None
#
#                   INPUT
# Code responsible for taking the user input
#
# Produces a help section if requested by user
#
# @return lowerInput STRING
# @return originalInput STRING
#


def userInput():
    originalInput = input("Please enter a query: ")
    lowerInput = originalInput.lower()

    while lowerInput in ['help']:
        print ("blank")
        originalInput = input("Please enter a new query: ")
        lowerInput = originalInput.lower()
    # insert help stuff here
    if lowerInput in ['exit']:
        exit()
    return lowerInput, originalInput
#
#                   TOKENIZER
# Code responsible for tokenizing the input
#
# Section also detects DATES and OPERATORS with RE
# as they are later removed by the punctuation removers
# Dates require ORA Format DD-MMM-YYYY
#
# @param lowerInput STRING
# @param originalInput STRING
#
# @return tokenInput LIST Input separated into list of words
# @return detectedDates LIST Dates in input in list of dates
# @return detectedOps LIST Operators in input in list of operators
#


def tokenizer(lowerInput, originalInput):
    print("Tokenizer:", sep="", end="", flush=True)

    # Extract Operators
    comparisonOps = re.compile('(>=|<=|<|>|=)')
    detectedOps = comparisonOps.findall(originalInput)

    # Extract Dates
    dateFind = re.compile('([1-3]?[0-9]\-\w{3}\-[0-9]{2})')
    detectedDates = dateFind.findall(originalInput)

    # Remove Punctuation
    translator = str.maketrans(dict.fromkeys(string.punctuation))
    noPunc = lowerInput.translate(translator)
    tokenInput = noPunc.split()
    print(" SUCCESS!")
    del lowerInput
    return tokenInput, detectedDates, detectedOps

#
#                   SYNONYMS
# Code responsible for replacing words with synonyms
#
# Detects appropriate words in input and replaces
# with input that is better understood in the domain
# or extra input that aids in query generation
#
# @param tokenInput LIST Input separated into list of words
#
# @return synonymReplacer LIST Input with replaced words
#


def synonymModule(tokenInput, detectedOps):
    print("Synonym Replacer:", sep="", end="", flush=True)
    synonymDict = {'staff': ('employees', 'first_name', 'last_name'),
                   'employee': 'employees', 'title': 'job_title',
                   'position': 'job_title', 'job': 'job_title',
                   'maximum': 'max', 'average': 'avg', 'minimum': 'min',
                   'salaries': 'salary', 'role': 'job_title',
                   'name': 'first_name', 'departmentid': 'dept_name',
                   'deptid': 'dept_name', 'earn': 'salary', 'earns': 'salary',
                   'hire': 'hire_date', 'hired': 'hire_date', 'over': '>',
                   'under': '<', 'earner': ('salary', 'employees',
                                            'first_name', 'last_name'),

                   'site': 'locationID', 'highest': 'max', 'lowest': 'min',
                   'most': 'max', 'least': 'min', 'largest': 'max',
                   'lowest': 'min'}
    operatorsFind = ['<', '>', '<=', '>=', '=']

    synonymReplacer = []
    for i, words in enumerate(tokenInput):
        if tokenInput[i] in synonymDict.keys():
            if synonymDict[tokenInput[i]] in operatorsFind:
                detectedOps.append(synonymDict[tokenInput[i]])
            # unpacks Tuples, for multi-word replacements
            if isinstance(synonymDict[tokenInput[i]], tuple):
                for v in synonymDict[tokenInput[i]]:
                    synonymReplacer.append(v)
            else:
                synonymReplacer.append(synonymDict[tokenInput[i]])
        else:
            synonymReplacer.append(tokenInput[i])
    del tokenInput
    print(" SUCCESS!")
    return synonymReplacer, detectedOps
#
#                   STOP WORDS
# Code responsible for removing stop words
#
# Detects stop words or useless words to the query
# generation component and removes them from the
# list of words.
#
# @see nltk.corpus
#
# @param synonymReplacer LIST list of words with input replaced
#
# @return tokenStop LIST list of words with stop words removed
#


def stopWordModule(synonymReplacer):
    print("Stop Word Remover:", sep="", end="", flush=True)
    stopListOmit = set(('example'))
    stopListContext = ['please', 'show', 'pull', 'records', 'named',
                       'any', 'all', 'called', 'anyall', 'provide', 'current',
                       'information', 'currently', 'us', 'work', 'working',
                       'company', 'could', 'see', 'business', 'send',
                       'details']
    stopListNLTK = set(stopwords.words('english')) - stopListOmit
    # populate as you go

    tokenStop = []
    for i, words in enumerate(synonymReplacer):
        if (synonymReplacer[i] not in stopListNLTK and
                synonymReplacer[i] not in stopListContext):
            tokenStop.append(synonymReplacer[i])

    print(" SUCCESS!")
    del synonymReplacer
    return tokenStop
#
#               KEY WORD LIST
# Code to detect key words of particular types
#
# Maps input words to attributes, entities, functions,
# words for order, numbers and leftover words.
#
# @param tokenStop list of words with stop words removed
#
# @return detectedAtts list of words detected as attributes in domain
# @return detectedEnts list of words detected as entities in domain
# @return detectedAggs list of words detected as function
# @return detectedNums list of numbers detected in input
# @return detectedOrder list of order words detected in input (ASC, DSC)
# @return leftOverWords list of words that were not mapped
# @return keyListAttribute  key-value pair mapping attributes to entities
#


def keyWordDetection(tokenStop):
    keyListEntity = ['employees', 'jobs', 'job_history',
                     'departments', 'locations']
    keyListAttribute = {'jobID': 'jobs', 'job_title': 'jobs',
                        'min_salary': 'jobs', 'max_salary': 'jobs',
                        'salary': 'employees', 'locationID': 'locations',
                        'address': 'locations', 'postcode': 'locations',
                        'city': 'locations', 'first_name': 'employees',
                        'last_name': 'employees', 'email': 'employees',
                        'phone': 'employees', 'hire_date': 'employees',
                        'commissionPCT': 'employees', 'managerID': 'employees',
                        'start_date': 'job_history', 'end_date': 'job_history',
                        'departmentID': 'departments',
                        'dept_name': 'departments'}
    keyListAgg = ['avg', 'max', 'min', 'count']
    # MOVE ME INTO SYNONYM REPLACER PLEASE....
    keyListOrder = {'order': 'ASC', 'order_by': 'ASC',
                    'ascending': 'ASC', 'descending': 'DSC',
                    'asc': 'ASC', 'dsc': 'DSC'}

    # Create the empty lists
    detectedAtts = []
    detectedEnts = []
    detectedAggs = []
    detectedNums = []
    detectedOrder = []
    leftOverWords = []

    # Iterate through words and assign a category
    for i, words in enumerate(tokenStop):
        if tokenStop[i] in keyListEntity:
            detectedEnts.append(tokenStop[i])
        elif (tokenStop[i] in keyListAttribute.keys()
                and not tokenStop[i] in detectedAtts):
            detectedAtts.append(tokenStop[i])
        elif tokenStop[i] in keyListAgg:
            detectedAggs.append(tokenStop[i])
        elif tokenStop[i].isdigit():
            detectedNums.append(tokenStop[i])
        elif tokenStop[i] in keyListOrder.keys():
            detectedOrder.append(keyListOrder[tokenStop[i]])
        else:
            leftOverWords.append(tokenStop[i])

    # If the attribute's entity was not detected, then automatically add it
    if detectedAtts:
        for i, words in enumerate(detectedAtts):
            if keyListAttribute[detectedAtts[i]] not in detectedEnts:
                detectedEnts.append(keyListAttribute[detectedAtts[i]])
    return(detectedAtts, detectedEnts, detectedAggs, detectedNums,
           detectedOrder, leftOverWords, keyListAttribute)


# Method to format parts of a string individually.
def queryFormat(template, **queryArg):
    for key, value in queryArg.items():
        temp = '{%s}' % key
        while True:
            pos = template.find(temp)
            if pos < 0:
                break
            template = template[:pos] + str(value) + \
                template[pos+len(temp):]
    return template

#
#               QUERY GENERATION
# Code responsible for construction of the query
#
# Using the categorised words to determine query
# components that need to be used. Makes use of queryFormat
#
# @see queryFormat
#
# @param detectedAtts list of words detected as attributes in domain
# @param detectedEnts list of words detected as entities in domain
# @param detectedAggs list of words detected as functions
# @param detectedNums list of numbers detected in input
# @param detectedOrder list of order words detected in input (ASC, DSC)
# @param leftOverWords list of words that were not mapped
# @param keyListAttribute key-value pair mapping attributes to entities
#
# @return templateQuery STRING Query generated as a string
#


def queryGeneration(detectedAtts, detectedEnts, detectedAggs,
                    detectedNums, detectedOrder, leftOverWords, detectedDates,
                    detectedOps, keyListAttribute):
    # Boolean to tell the query to stop if it is not going to succeed
    #   Failure cases e.g.: No entities exist (no FROM)

    successfulQuery = True
    templateQuery = "SELECT"

    # AGG/FUNCTION WORDS:
    if detectedAggs:
        templateQuery += " {agg}"
        templateQuery = queryFormat(templateQuery,
                                    agg=detectedAggs[0])
    else:
        templateQuery = queryFormat(templateQuery, agg=' ')

    # ATTRIBUTES
    for i, words in enumerate(detectedAtts):
        if i == 0:
            templateQuery += "{att}"
            templateQuery = queryFormat(templateQuery,
                                        att='('+detectedAtts[0]+')')
        else:
            templateQuery += ", {att}"
            templateQuery = queryFormat(templateQuery,
                                        att=detectedAtts[i])

    if not detectedAtts:
        templateQuery += ' *'

    # ENTITIES
    templateQuery += " FROM {ent}"
    if not detectedEnts:
        # Query Generation stops here if FALSE.
        # No SELECT is possible without FROM
        successfulQuery = False

    # TABLE JOINS
    # Requires correct ordering of entities in input
    if successfulQuery:
        primaryKeyQuery = "SELECT columns.column_name \
                            FROM all_constraints constraint, \
                            all_cons_columns columns \
                            WHERE columns.table_name = '{TABLENAME}' \
                            AND constraint.constraint_type = 'P' \
                            AND constraint.constraint_name = \
                            columns.constraint_name \
                            AND constraint.owner != 'HR' \
                            ORDER BY columns.table_name, columns.position"

        for i, words in enumerate(detectedEnts):
            if i == 0:
                entQuery = (detectedEnts[i].upper())
                curs.execute(primaryKeyQuery.format(TABLENAME=entQuery))
                OrigPK = curs.fetchone()[0]
                templateQuery = queryFormat(templateQuery, ent=detectedEnts[0])
            else:
                entQuery = (detectedEnts[i].upper())
                curs.execute(primaryKeyQuery.format(TABLENAME=entQuery))
                PK = curs.fetchone()[0]
                templateQuery += " JOIN {entjoin} ON {entity}.{origpk} \
                                    = {entjoin}.{pk}"
                templateQuery = queryFormat(templateQuery,
                                            entjoin=detectedEnts[i],
                                            entity=detectedEnts[0],
                                            origpk=PK, pk=PK)

    # WHERE
    # Determines DATA TYPE of column in order to generate query
    # Only works for NUMBERS and DATES
    if leftOverWords:
        for i, words in enumerate(leftOverWords):
            print()
            print('I\'ve found \'%s\' in your input. \
                    Please tell me what it is' % leftOverWords[i])
            print('Enter the following number for the\
                    appropriate attribute')
            print('1. First name')
            print('2. Last name')
            print('3. Location')
            print('4. Department')
            print('5. Ignore the word')
            numInput = int(input('Enter a number: '))
            if numInput == 1:
                if 'employees' not in detectedEnts:
                    templateQuery += " NATURAL JOIN Employees" 
                templateQuery += " WHERE {att} = '{val}'"
                templateQuery = queryFormat(templateQuery,
                                            att="first_name",
                                            val=leftOverWords[i])
            elif numInput == 2:
                templateQuery += " WHERE {att} = '{val}'"
                templateQuery = queryFormat(templateQuery,
                                            att="last_name",
                                            val=leftOverWords[i])
            elif numInput == 3:
                if 'locations' not in detectedEnts:
                    if 'departments' not in detectedEnts:
                        templateQuery += " JOIN Departments ON \
                        Employees.DepartmentID = Departments.DepartmentID"
                    templateQuery += " JOIN Locations ON departments.locationID \
                    = locations.locationID"
                storeQuery = templateQuery
                templateQuery += " WHERE {att} = '{val}'"
                storeQuery += " WHERE {att} = ''{val}''"
                templateQuery = queryFormat(templateQuery,
                                            att="locations.city",
                                            val=leftOverWords[i])
                storeQuery = queryFormat(templateQuery,
                                         att="locations.city",
                                         val=leftOverWords[i])
            elif numInput == 4:
                if 'departments' not in detectedEnts:
                    templateQuery += " JOIN Departments ON \
                    Employees.DepartmentID = Departments.DepartmentID"
                    templateQuery += " WHERE {att} = '{val}'"
                    templateQuery = queryFormat(templateQuery,
                                                att="dept_name",
                                                val=leftOverWords[i])
            elif numInput == 5:
                pass

    if detectedOps and detectedNums:
        typeQuery = "SELECT data_type FROM all_tab_columns \
                    WHERE table_name = '{TABLENAME}' \
                    AND column_name = '{COLUMN}'"
        for i, words in enumerate(detectedAtts):
            curs.execute(queryFormat(typeQuery,
                                     TABLENAME=((keyListAttribute[detectedAtts[i]])
                                                .upper()),
                                     COLUMN=detectedAtts[i].upper()))
            dataType = curs.fetchone()[0]
            if dataType == 'NUMBER':
                templateQuery += " WHERE {att} {ops} {val}"
                templateQuery = queryFormat(templateQuery, att=detectedAtts[i],
                                            ops=detectedOps[0],
                                            val=detectedNums[0])
    elif detectedDates and detectedAtts:
        typeQuery = "SELECT data_type FROM all_tab_columns WHERE table_name = '{TABLENAME}' \
                    AND column_name = '{COLUMN}'"
        for i, words in enumerate(detectedAtts):
            curs.execute(queryFormat(typeQuery,
                                     TABLENAME=((keyListAttribute[detectedAtts[i]])
                                                .upper()),
                                     COLUMN=detectedAtts[i].upper()))
            dataType = curs.fetchone()[0]
            if dataType == 'DATE':
                if len(detectedDates) >= 2:
                    templateQuery += " WHERE {att} BETWEEN \
                                     '{val1}' AND '{val2}'"
                    templateQuery = queryFormat(templateQuery,
                                                att=detectedAtts[i],
                                                val1=detectedDates[0],
                                                val2=detectedDates[1])
                else:
                    templateQuery += " WHERE {att} {ops} '{val}'"
                    if detectedOps:
                        templateQuery = queryFormat(templateQuery,
                                                    ops=detectedOps[0])
                    else:
                        templateQuery = queryFormat(templateQuery,
                                                    att=detectedAtts[i],
                                                    val=detectedDates[0])

    # GROUP BY
    # Part two of Agg/Function words - some require grouping.
    if detectedAggs and successfulQuery and len(detectedAtts) >= 2:
        templateQuery += " GROUP BY {attgroup}"
        templateQuery = queryFormat(templateQuery,
                                    attgroup=detectedAtts[1])

    # ORDER BY
    if detectedOrder and successfulQuery:
        templateQuery += " ORDER BY {orderatt} {order}"
        templateQuery = queryFormat(templateQuery,
                                    orderatt=detectedAtts[0],
                                    order=detectedOrder[0])

    # Failure case
    if not successfulQuery:
        print()
        print("A successful query could not be constructed from your input.")
        print("Exiting in 5")
        time.sleep(5)
        main()

    print(templateQuery)
    return templateQuery
#
#               QUERY EXECUTION
# Code to execute the query
#
# @param templateQuery STRING Query generated as a string
#


def queryExec(templateQuery):
    print()
    print("Query to run: %s" % templateQuery)
    print()
    print()
    curs.execute(templateQuery)

    # Print column headings
    for i in curs.description:
        print(i[0], sep="", end="    ", flush=True)

    print()
    # Print rows individually
    for row in curs:
        print(row)
    return None
#
#               QUERY LOGGING
# Code to log the scenario
#
# Saves the input, the query generated, and a user confirmation
#
# @param originalInput STRING Original user input
# @param templateQuery STRING Query generated as a string
#


def queryLog(originalInput, templateQuery):
    print()
    print()
    print("Is this the output you expected?")
    userConf = input("Please enter only Y or N:  ")
    userConf = userConf.lower()

    # Check if it exists already in the log
    validQuery = "SELECT OrigInput FROM Log"
    curs.execute(validQuery)
    origInputArray = []
    origInputArray = [word for word, in curs.fetchall()]

    for i, words in enumerate(origInputArray):
        origInputArray[i] = origInputArray[i].lower()

    if originalInput.lower() not in origInputArray:
        print("Thank you for the new query!")
        countQuery = "SELECT max(LogID) FROM Log"
        curs.execute(countQuery)
        maxCount = curs.fetchone()[0]
        maxCount = maxCount+1
        print(maxCount)
        confQuery = "INSERT INTO Log (LogID, OrigInput, QueryRan, UserConf) \
                    VALUES (%s, '%s', '%s', '%s')" % (maxCount, \
                                                      originalInput, \
                                                      templateQuery, \
                                                      userConf)
        print(confQuery)
        curs.execute(confQuery)
        curs.execute("commit")
        time.sleep(1)
    else:
        print("Thank you, this input has been logged.")
    del originalInput
    return None
#
#                   MAIN
# Controls the data flow throughout the application
#


def main():
    databaseConnection()
    lowerInput, originalInput = userInput()
    (tokenInput, detectedDates,
     detectedOps) = tokenizer(lowerInput, originalInput)
    synonymReplacer, detectedOps = synonymModule(tokenInput, detectedOps)
    tokenStop = stopWordModule(synonymReplacer)
    (detectedAtts, detectedEnts, detectedAggs, detectedNums,
     detectedOrder, leftOverWords,
     keyListAttribute) = keyWordDetection(tokenStop)
    templateQuery = queryGeneration(detectedAtts, detectedEnts,
                                    detectedAggs, detectedNums, detectedOrder,
                                    leftOverWords, detectedDates, detectedOps,
                                    keyListAttribute)
    queryExec(templateQuery)
    queryLog(originalInput, templateQuery)


if __name__ == '__main__':
    main()

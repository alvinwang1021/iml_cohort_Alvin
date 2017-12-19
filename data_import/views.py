from django.shortcuts import render
from django.conf import settings
from django.core.files.storage import FileSystemStorage
import numpy as np

# from .models import Document 
from .forms import DocumentForm
import pandas as pd
import os
import shutil
from scipy import sparse, io


file_upload_dir = os.path.join(settings.BASE_DIR, 'data')
fs = FileSystemStorage(location=file_upload_dir)


def handle_uploaded_file(f):
    features=pd.read_csv(f,nrows=2)
    return features

#accept the file, process it and store it locally in csv format
def process_file(f):
    
    rawdata = pd.read_csv(f)
   
    df = rawdata.drop([0])
    df["1"] = df["1"].astype(int)
    
    IDarr = df['1'].unique()
    
    DDXlist = [ ]
    DDXvalue = ""
    
    for idno in IDarr:
        dfDDXbyID = df[df["1"] == idno].iloc[:,95:195]
        dfIni = dfDDXbyID['95']
        for col in range (96, 195):
            dfFin = pd.concat([dfIni,dfDDXbyID[str(col)]])
            dfIni = dfFin
        ''' concat col by col'''
        diglist = dfFin.dropna().tolist()
        
        value = ','.join([str(code) for code in diglist])
        #print ("value", value)
        DDXvalue = DDXvalue + value + ","
        '''DDXvalue is a long string including all DDX'''
        #print ("DDXvalue", DDXvalue)
        DDXlist.append(diglist)
    
    DDXvalueSeparate = [x for x in DDXvalue.split(",") if x is not '']
    DDXsetUnique = set(DDXvalueSeparate)
    #print ('DDXsetUnique', DDXsetUnique)
    DDXlistUnique = list(DDXsetUnique)
    '''1d list to store all distinct DDX'''
    #print ('DDXlistUnique', DDXlistUnique)
    dfDDX = pd.DataFrame(DDXlist)
    #dfID = pd.DataFrame(IDarr)
    #print dfDDX
    #print dfID
    

    #diag_dict = pd.read_csv('data/D_ICD_DIAGNOSES.csv')
    #doc = pd.read_csv(f)
    #new_doc = doc[new_features]
    #print new_doc, "\n"
    #distinct_dias = np.asarray(DDXlistUnique)
    #print type(distinct_dias)
    distinct_pates = IDarr
    #print type(distinct_pates)
    #print len(distinct_pates)
    #diags = []
    diags_desc = []
    data = []
    #diaList = distinct_dias.tolist()
    #print ('diaList', diaList)
    #print ('asarray', distinct_dias)
    
    for i in range (0, len(distinct_pates)):
        #print p
        vec = np.zeros(len(DDXlistUnique),dtype=int)
        #ps = new_doc[new_doc['PATIENT_ID']==p]
        #print ps.DIAGNOSES_CODE
        str_diags_codes = '\t'.join([str(code) for code in dfDDX.loc[i].dropna().tolist()])
        
        #print str_diags_codes
        #descs = []
        for code in dfDDX.loc[i].dropna().tolist():
            #print code
            index = DDXlistUnique.index(code)
            vec[index] += 1
            #desc = diag_dict[diag_dict['ICD9_CODE']==code].SHORT_TITLE
            #if (not desc.empty):
                #descs.append(desc.iloc[0])
            
        #str_diags_desc = '\t'.join(descs)
        diags_desc.append(str_diags_codes)
        #print vec.shape
        data.append(vec)
        #diags.append(str_diags_codes)
        
        
    #print len(diags)
    sparse_data = sparse.csr_matrix(data)

    file_path_data = os.path.join(settings.BASE_DIR, 'data/outcome_data')
    file_path_pationid = os.path.join(settings.BASE_DIR, 'data/outcome_pation.csv')
    file_path_deid = os.path.join(settings.BASE_DIR, 'data/outcome_deid.csv')
    #file_path_diags = os.path.join(settings.BASE_DIR, 'data/outcome_diags.csv')
    file_path_diags_desc = os.path.join(settings.BASE_DIR, 'data/outcome_diags_desc.csv')
  

    #new_data = pd.DataFrame(data)
    distinct_dias_data = pd.DataFrame(DDXlistUnique)
    distinct_pates_data = pd.DataFrame(distinct_pates)
     
    #newm = io.mmread(file)
    io.mmwrite(file_path_data, sparse_data)
    distinct_dias_data.to_csv(file_path_deid,header=False)
    distinct_pates_data.to_csv(file_path_pationid,header=False)
    #pd.DataFrame(data=diags,columns=['diags']).to_csv(file_path_diags)
    pd.DataFrame(data=diags_desc,columns=['diags']).to_csv(file_path_diags_desc)


def renew(request):
    if request.method == 'POST':
        new_features = request.POST.getlist('new_features')
        file_path = 'C:\\Users\\Alvin UTS\\Desktop\\Test_Alvin.csv'
        
        
        process_file(file_path)
        content = {'Title': "Step 3: Feature Processing",
                   "listId":"li3",
                   'features': new_features} 
        return render(
            request,
            'data_import/stp3-fea-processing.html',
            content
        )
def index(request):
    content = {'Title': "Step 1: Upload Data",
                   "listId":"li1"}    
    return render(request, 'data_import/stp1-import.html', content)
    

def upload(request):
    # Handle file upload
    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            print ("request files in list-----",request.FILES)
            docfile = request.FILES['docfile']
            features = handle_uploaded_file(docfile)
            file_upload_dir = os.path.join(settings.BASE_DIR, 'tmp')
            fs = FileSystemStorage(location=file_upload_dir)
            if os.path.exists(file_upload_dir): 
                shutil.rmtree(file_upload_dir)
            fs.save("tmp.csv", docfile)
            
            content = {'Title': "Step 2: Feature Selection",
                   "listId":"li2",
                   'features': features} 
            return render(
                request,
                'data_import/stp2-fea-selection.html',
                content
            )

    else:
        content = {'Title': "Step 1: Upload Data",
                   "listId":"li1"}    
        return render(request, 'data_import/stp1-import.html', content)

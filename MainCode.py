"""
Victor Hugo Resende Lima
vhugoreslim@gmail.com

Esse código necessita dos seguintes pacotes nas respectivas versões:
Pillow==9.0.1
scipy==1.7.3
streamlit==1.5.0
click==8
"""
import streamlit as st
import numpy as np
import sys
from streamlit import cli as stcli
from scipy.integrate import quad #Single integral
from scipy.integrate import dblquad
from PIL import Image

def main():
    #criando 3 colunas
    col1, col2, col3= st.columns(3)
    foto = Image.open('randomen.png')
    #st.sidebar.image("randomen.png", use_column_width=True)
    #inserindo na coluna 2
    col2.image(foto, use_column_width=True)
    #O código abaixo centraliza e atribui cor
    st.markdown("<h2 style='text-align: center; color: #306754;'>Hybrid Inspection and Age-Based Policy with Inspector Assignment</h2>", unsafe_allow_html=True)
    
    st.markdown("""
        <div style="background-color: #F3F3F3; padding: 10px; text-align: center;">
          <p style="font-size: 20px; font-weight: bold;">A Delay-Time Model for Non-Periodic Inspection Intervals and Inspector Team Assignment</p>
          <p style="font-size: 15px;">By: Victor H. R. Lima & Cristiano A. V. Cavalcante</p>
        </div>
        """, unsafe_allow_html=True)

    menu = ["Cost-rate", "Information", "Website"]
    
    choice = st.sidebar.selectbox("Select here", menu)
    
    if choice == menu[0]:
        st.header(menu[0])
        if 'num_columns' not in st.session_state:
            st.session_state.num_columns = 2
        def add_column():
            st.session_state.num_columns += 1
        def remove_column():
            if st.session_state.num_columns > 1:
                st.session_state.num_columns -= 1
        
        st.subheader("Insert the parameter values below:")
        
        Eta1=st.number_input("Insert the characteristic life of the weak component (η\u2081)", min_value = 0.0, value = 3.0, help="This parameter specifies the scale parameter for the Weibull distribution, representing the defect arrival for the weaker component.")
        Beta1=st.number_input("Insert the shape parameter of the weak component (β\u2082)", min_value = 1.0, max_value=5.0, value = 2.5, help="This parameter specifies the shape parameter for the Weibull distribution, representing the defect arrival for the weaker component.")
        Eta2=st.number_input("Insert the characteristic life of the strong component (η\u2081)", min_value = 3.0, value = 18.0, help="This parameter specifies the scale parameter for the Weibull distribution, representing the defect arrival for the stronger component.")
        Beta2=st.number_input("Insert the shape parameter of the strong component (β\u2082)", min_value = 1.0, max_value=5.0, value = 5.0, help="This parameter specifies the shape parameter for the Weibull distribution, representing the defect arrival for the stronger component.")
        p=st.number_input("Insert the mixture parameter (p)", min_value = 0.0, value = 0.10, help="This parameter indicates the proportion of the weaker component within the total population of components.")
        Lambda=st.number_input("Insert the rate of the exponential distribution for delay-time (λ)", min_value = 0.0, value = 2.0, help="This parameter defines the rate of the Exponential distribution, which governs the transition from the defective to the failed state of a component.")
        Cr=st.number_input("Insert cost of replacement (inspections and age-based) (C\u02b3)", min_value = 0.5, value = 1.0, help="This parameter represents the cost associated with preventive replacements, whether performed during inspections or when the age-based threshold is reached.")
        Cf=st.number_input("Insert cost of failure (C\u1da0)", min_value = 1.0, value = 10.0, help="This parameter represents the replacement cost incurred when a component fails.")
        
        col1, col2 = st.columns(2)

        # Botões com balões informativos, cada um em uma coluna
        with col1:
            st.button("Add Repairperson", on_click=add_column, help="You should add columns to the parameters of the repairperson as you want (each column is related to one repairperson).")
        
        with col2:
            st.button("Remove Repairperson", on_click=remove_column)

        FixedCosts=[]
        Ci=[]
        Alpha=[]
        Beta=[]
        columns = st.columns(st.session_state.num_columns)

        for i, col in enumerate(columns):
            col.write(f"**Inspector {i+1}:**") 
            FixedCosts.append(col.number_input(f"Fixed Cost (C\u02b0)", min_value=0.0, value=0.1, key=f"FixedCosts_{i}", help="This parameter defines the cost related to the hiring of the repairperson."))
            Ci.append(col.number_input(f"Inspection Cost (C\u2071)", min_value=0.0, value=0.15, key=f"Ci_{i}", help="This parameter represents the cost of conducting a single inspection by this repairperson."))
            Alpha.append(col.number_input(f"False-Positive Percentage (α)", min_value=0.0, value=0.1, key=f"Alpha_{i}", help="This parameter defines the probability that, during an inspection, the repairperson will incorrectly classify a component as defective when it is actually not."))
            Beta.append(col.number_input(f"False-Negative Percentage (ε)", min_value=0.0, value=0.05, key=f"Beta_{i}", help="This parameter defines the probability that, during an inspection, the repairperson will incorrectly classify a component as good when it is actually defective."))
        
        Y=[-1]
        st.subheader("Insert the variable values below:")
        K=int(st.text_input("Insert the number of inspections (K)", value=4))
        delta=st.text_input("Insert the inspection moments (Δ), following the example below",value="2,00 4,00 8,00 10,00", key=f"Delta")
        Delta=[float(x.replace(",", ".")) for x in delta.split()]
        Delta.insert(0,0)
        for i, col in enumerate(st.columns(K)):
            col.write(f"**{i+1}-th inspection:**")
            Y.append(col.number_input("Rep. Assgn. (Y)", min_value=1, max_value=len(FixedCosts), value=1, step=1, key=f"Y_{i}") - 1)
        T = st.number_input("Insert the moment for the age-based preventive action (T)", min_value=Delta[-1], value= 12.0)
        
        botao = st.button("Get cost-rate")
        if botao:
            def KD_KT(K,delta,Y,T):
                ############Defect arrival component 1#####################################
                def f01(x):
                    return (Beta1/Eta1)*((x/Eta1)**(Beta1-1))*np.exp(-(x/Eta1)**Beta1)
                ############Defect arrival component 2#####################################
                def f02(x):#
                    return (Beta2/Eta2)*((x/Eta2)**(Beta2-1))*np.exp(-(x/Eta2)**Beta2)
                ###########Mixture for defect arrival######################################
                def fx(x):
                    return (p*f01(x))+((1-p)*f02(x))
                ##########Delay-time distribution##########################################
                def fh(h):
                    return Lambda*np.exp(-Lambda*h)
                ##########Cumulative for defect arrival####################################
                def Fx(x):
                    return (p*(1-np.exp(-(x/Eta1)**Beta1)))+((1-p)*(1-np.exp(-(x/Eta2)**Beta2)))
                #########Reliability function for defect arrival###########################
                def Rx(x):
                    return 1-Fx(x)
                ##########Cumulative function delay-time###################################
                def Fh(h):
                    return 1-np.exp(-Lambda*h)
                ##########Reliability function delay-time##################################
                def Rh(h):
                    return np.exp(-Lambda*h)
    
                #####OBS: THE SOLUTION CONTAINS DELTA[0]=0, Y[0]=-1
    
                ############Scenario 1: Defect arrival and failure between inspections#####
                def C1():
                    PROB1=0
                    EC1=0
                    EL1=0
                    for i in range(0, K):
                        InspectionCost=0
                        TotalAlpha=1
                        for j in range(0,i+1,1):
                            if (j!=0):
                                InspectionCost+=Ci[Y[j]]
                                TotalAlpha*=(1-Alpha[Y[j]])
                        PROB1+=TotalAlpha*(dblquad(lambda h, x: fx(x)*fh(h), delta[i], (delta[i+1]),0,lambda x:(delta[i+1])-x)[0])
                        EL1+=TotalAlpha*(dblquad(lambda h, x: (x+h)*fx(x)*fh(h), delta[i], (delta[i+1]),0,lambda x:(delta[i+1])-x)[0])
                        EC1+=(InspectionCost+Cf)*(TotalAlpha*(dblquad(lambda h, x: fx(x)*fh(h), delta[i], (delta[i+1]),0,lambda x:(delta[i+1])-x)[0]))
                    return PROB1, EC1, EL1
                
                ############Scenario 2: Defect arrival and surviving until next inspection without error at inspection####
                def C2():
                    PROB2=0
                    EC2=0
                    EL2=0
                    for i in range(0, K):
                        InspectionCost=0
                        TotalAlpha=1
                        for j in range(0,i+1,1):
                            if (j!=0):
                                InspectionCost+=Ci[Y[j]]
                                TotalAlpha*=(1-Alpha[Y[j]])
                        #####Counting the last inspection where there is no false positive#########
                        InspectionCost+=Ci[Y[i+1]]
                        ###################################################################
                        PROB2+=TotalAlpha*(1-Beta[Y[i+1]])*(quad(lambda x: fx(x)*(1-Fh((delta[i+1])-x)),delta[i], (delta[i+1]))[0])
                        EC2+=(InspectionCost+Cr)*(TotalAlpha*(1-Beta[Y[i+1]])*(quad(lambda x: fx(x)*(1-Fh((delta[i+1])-x)),delta[i], (delta[i+1]))[0]))
                        EL2+=(delta[i+1])*(TotalAlpha*(1-Beta[Y[i+1]])*(quad(lambda x: fx(x)*(1-Fh((delta[i+1])-x)),delta[i], (delta[i+1]))[0]))
                    return PROB2, EC2, EL2
                
                ##########Scenario 3: Defect arrival after inspections and failure#########
                def C3():
                    InspectionCost=0
                    TotalAlpha=1
                    for j in range(0,K+1,1):
                        if (j!=0):
                            InspectionCost+=Ci[Y[j]]
                            TotalAlpha*=(1-Alpha[Y[j]])
                    PROB3=TotalAlpha*(dblquad(lambda h, x: fx(x)*fh(h), delta[K], T,0,lambda x:T-x)[0])
                    EC3=(InspectionCost+Cf)*PROB3
                    EL3=TotalAlpha*(dblquad(lambda h, x: (x+h)*fx(x)*fh(h), delta[K], T,0,lambda x:T-x)[0])
                    return PROB3, EC3, EL3
                
                ###########Scenario 4: Defect arrival after inspections and preventive at T####
                def C4():
                    InspectionCost=0
                    TotalAlpha=1
                    for j in range(0,K+1,1):
                        if (j!=0):
                            InspectionCost+=Ci[Y[j]]
                            TotalAlpha*=(1-Alpha[Y[j]])
                    PROB4=TotalAlpha*quad(lambda x: fx(x)*(1-Fh(T-x)),delta[K],T)[0]
                    EC4=(InspectionCost+Cr)*PROB4
                    EL4=T*PROB4
                    return PROB4, EC4, EL4
                
                ##########Scenario 5: No defect arrival####################################
                def C5():
                    InspectionCost=0
                    TotalAlpha=1
                    for j in range(0,K+1,1):
                        if (j!=0):
                            InspectionCost+=Ci[Y[j]]
                            TotalAlpha*=(1-Alpha[Y[j]])
                    PROB5=TotalAlpha*Rx(T)
                    EC5=(InspectionCost+Cr)*PROB5
                    EL5=T*PROB5
                    return PROB5, EC5, EL5
                
                ##########Scenario 6: Defect arrival and sucessive false negatives at inspections#####
                def C6():
                    PROB6=0
                    EC6=0
                    EL6=0
                    for i in range(0, K-1):
                        #####Computing the total alpha#############
                        InspectionCost1=0
                        TotalAlpha=1
                        for j in range(0,i+1,1):
                            if (j!=0):
                                InspectionCost1+=Ci[Y[j]]
                                TotalAlpha*=(1-Alpha[Y[j]])
                        ###########################################
                        for j in range(i+1, K):
                            #####Computing the total beta##########
                            InspectionCost=InspectionCost1
                            TotalBeta=1
                            for k in range(i+1,j+1,1):
                                InspectionCost+=Ci[Y[k]]
                                TotalBeta*=Beta[Y[k]]
                            ###############################################################
                            PROB6+=TotalAlpha*TotalBeta*(dblquad(lambda h, x: fx(x)*fh(h), delta[i], (delta[i+1]),lambda x:(delta[j])-x,lambda x:(delta[j+1])-x)[0])
                            EL6+=TotalAlpha*TotalBeta*(dblquad(lambda h, x: (x+h)*fx(x)*fh(h), delta[i], (delta[i+1]),lambda x:(delta[j])-x,lambda x:(delta[j+1])-x)[0])
                            EC6+=(InspectionCost+Cf)*(TotalAlpha*TotalBeta*(dblquad(lambda h, x: fx(x)*fh(h), delta[i], (delta[i+1]),lambda x:(delta[j])-x,lambda x:(delta[j+1])-x)[0]))
                    return PROB6, EC6, EL6
                
                ##########Scenario 7: Defect arrival inside inspection phase with false negatives and a true positive####
                def C7():
                    PROB7=0
                    EC7=0
                    EL7=0
                    for i in range(0, K-1):
                        #######Computing the total alpha##############################
                        InspectionCost1=0
                        TotalAlpha=1
                        for j in range(0,i+1,1):
                            if (j!=0):
                                InspectionCost1+=Ci[Y[j]]
                                TotalAlpha*=(1-Alpha[Y[j]])
                        ##############################################################
                        for j in range(i+2,K+1,1):
                            InspectionCost=InspectionCost1
                            TotalBeta=1
                            for k in range(i+1,j):
                                InspectionCost+=Ci[Y[k]]
                                TotalBeta*=Beta[Y[k]]
                            ######Counting the last inspection#############################
                            InspectionCost+=Ci[Y[j]]
                            ###############################################################
                            PROB7+=TotalAlpha*TotalBeta*(1-Beta[Y[j]])*(quad(lambda x: fx(x)*Rh((delta[j])-x),delta[i], (delta[i+1]))[0])
                            EC7+=(InspectionCost+Cr)*(TotalAlpha*TotalBeta*(1-Beta[Y[j]])*(quad(lambda x: fx(x)*Rh((delta[j])-x),delta[i], (delta[i+1]))[0]))
                            EL7+=(delta[j])*(TotalAlpha*TotalBeta*(1-Beta[Y[j]])*(quad(lambda x: fx(x)*Rh((delta[j])-x),delta[i], (delta[i+1]))[0]))
                    return PROB7, EC7, EL7
                
                ##########Scenario 8: False positive at inspection########################
                def C8():
                    PROB8=0
                    EC8=0
                    EL8=0
                    for i in range(0,K):
                        TotalAlpha=1
                        InspectionCost=0
                        for j in range(0,i+1,1):
                            if (j!=0):
                                InspectionCost+=Ci[Y[j]]
                                TotalAlpha*=(1-Alpha[Y[j]])
                        InspectionCost+=Ci[Y[i+1]]
                        PROB8+=TotalAlpha*Alpha[Y[i+1]]*Rx(delta[i+1])
                        EC8+=(InspectionCost+Cr)*TotalAlpha*Alpha[Y[i+1]]*Rx(delta[i+1])
                        EL8+=(delta[i+1]*(TotalAlpha*Alpha[Y[i+1]]*Rx(delta[i+1])))
                    return PROB8, EC8, EL8
                
                ##########Scenario 9: Sucessive false negatives and failure after inspections#####
                def C9():
                    PROB9=0
                    EC9=0
                    EL9=0
                    for i in range(0,K):
                        ######Counting inspections before i############################
                        InspectionCost=0
                        TotalAlpha=1
                        for j in range(0,i+1):
                            if (j!=0):
                                InspectionCost+=Ci[Y[j]]
                                TotalAlpha*=(1-Alpha[Y[j]])
                        ########COunting inspections after i until K-th####################
                        TotalBeta=1
                        for j in range(i+1,K+1,1):
                            InspectionCost+=Ci[Y[j]]
                            TotalBeta*=Beta[Y[j]]
                        PROB9+=(TotalAlpha*TotalBeta*(dblquad(lambda h, x: fx(x)*fh(h), delta[i], delta[i+1],lambda x: delta[K]-x, lambda x:T-x)[0]))
                        EC9+=(InspectionCost+Cf)*((TotalAlpha*TotalBeta*(dblquad(lambda h, x: fx(x)*fh(h), delta[i], delta[i+1],lambda x:delta[K]-x, lambda x:T-x)[0])))
                        EL9+=((TotalAlpha*TotalBeta*(dblquad(lambda h, x: (x+h)*fx(x)*fh(h), delta[i], delta[i+1],lambda x:delta[K]-x, lambda x:T-x)[0])))
                    return PROB9, EC9, EL9
                
                #########Scenario 10: Sucessive false negatives and renovation at T########
                def C10():
                    PROB10=0
                    EC10=0
                    EL10=0
                    for i in range(0,K):
                        #######Counting inspections before i###############################
                        InspectionCost=0
                        TotalAlpha=1
                        for j in range(0,i+1):
                            if (j!=0):
                                InspectionCost+=Ci[Y[j]]
                                TotalAlpha*=(1-Alpha[Y[j]])
                        #######Counting inspections after i until K-th#####################
                        TotalBeta=1
                        for j in range(i+1,K+1,1):
                            InspectionCost+=Ci[Y[j]]
                            TotalBeta*=Beta[Y[j]]
                        PROB10+=TotalAlpha*TotalBeta*(quad(lambda x: fx(x)*Rh(T-x),delta[i], (delta[i+1]))[0])
                        EC10+=(InspectionCost+Cr)*(TotalAlpha*TotalBeta*(quad(lambda x: fx(x)*Rh(T-x),delta[i], (delta[i+1]))[0]))
                        EL10+=T*(TotalAlpha*TotalBeta*(quad(lambda x: fx(x)*Rh(T-x),delta[i], (delta[i+1]))[0]))
                    return PROB10, EC10, EL10
                
                ########Defining variables based on previous functions#####################
                C1=C1()
                C2=C2()
                C3=C3()
                C4=C4()
                C5=C5()
                C6=C6()
                C7=C7()
                C8=C8()
                C9=C9()
                C10=C10()
                
                ########Defining cost and life based on previous scenarios#################
                # TOTAL_PB=C1[0]+C2[0]+C3[0]+C4[0]+C5[0]+C6[0]+C7[0]+C8[0]+C9[0]+C10[0]
                TOTAL_EC=C1[1]+C2[1]+C3[1]+C4[1]+C5[1]+C6[1]+C7[1]+C8[1]+C9[1]+C10[1]
                TOTAL_EL=C1[2]+C2[2]+C3[2]+C4[2]+C5[2]+C6[2]+C7[2]+C8[2]+C9[2]+C10[2]
                ########Increasing cost with the fixed cost of the inspector###############
                Used=[]
                for i in range(0,len(FixedCosts),1):
                    Used.append(0)
                for i in range(1,len(Y),1):
                    Used[Y[i]]+=1
                for i in range(0,len(FixedCosts),1):
                    if (Used[i]>0):
                        TOTAL_EC+=FixedCosts[i]
                return TOTAL_EC/TOTAL_EL
            ################################################################
            st.write("---RESULT---")
            st.write("Cost-rate", KD_KT(K, Delta, Y, T))
            
    if choice == menu[1]:
        st.header(menu[1])
        st.write("<h6 style='text-align: justify; color: Blue Jay;'>This app is dedicated to computing the cost rate for a hybrid inspection and age-based maintenance policy with inspector assignments. We assume a single system operating under Delay-Time Modeling (DTM) with two types of components, each having distinct defect arrival distributions. Component renovation occurs either after a failure (corrective maintenance) or during inspections, once a defect is detected or if the age-based threshold is reached (preventive maintenance). Inspectors vary in their costs (contracting fees and unitary costs for performing inspections) and their error rates (false positives and false negatives). This app emphasizes the importance of optimally selecting inspectors to minimize the cost-rate.</h6>", unsafe_allow_html=True)
        st.write("<h6 style='text-align: justify; color: Blue Jay;'>The app computes the cost rate for a specific solution—defined by inspection intervals (Δ), inspector assignments (Y), and the age-based threshold (T).</h6>", unsafe_allow_html=True)
        st.write("<h6 style='text-align: justify; color: Blue Jay;'>For further questions or information on finding the optimal solution, please contact one of the email addresses below.</h6>", unsafe_allow_html=True)
        
        st.write('''

v.h.r.lima@random.org.br

c.a.v.cavalcante@random.org.br

''' .format(chr(948), chr(948), chr(948), chr(948), chr(948)))       
    if choice==menu[2]:
        st.header(menu[2])
        
        st.write('''The Research Group on Risk and Decision Analysis in Operations and Maintenance was created in 2012 
                 in order to bring together different researchers who work in the following areas: risk, maintenance a
                 nd operation modelling. Learn more about it through our website.''')
        st.markdown('[Click here to be redirected to our website](https://sites.ufpe.br/random/#page-top)',False)        
if st._is_running_with_streamlit:
    main()
else:
    sys.argv = ["streamlit", "run", sys.argv[0]]
    sys.exit(stcli.main())

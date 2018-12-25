import os
import shutil

def classify():
    with open("log.txt", "r+") as f:
        for line in f:
            dirname = line.split('/')[-1][:42]
            try:
                if not os.path.exists('contracts/'+dirname):
                    os.mkdir('contracts/'+dirname)
                    shutil.move('verified_contracts/'+dirname+'.sol', 'contracts/'+dirname+'/')
                    shutil.move('verified_contract_bins/'+dirname+'.bin', 'contracts/'+dirname+'/')
                    shutil.move('verified_contract_abis/'+dirname+'.abi', 'contracts/'+dirname+'/')
                    if os.path.exists('verified_contract_constructorparams/'+dirname+'.constructorparams'):
                        shutil.move('verified_contract_constructorparams/'+dirname+'.constructorparams','contracts/' + dirname + '/')
                    if os.path.exists('verified_contract_libraryparams/'+dirname+'.libraryparams'):
                        shutil.move('verified_contract_libraryparams/'+dirname+'.libraryparams', 'contracts/'+dirname+'/')
                    print(dirname+" move successfully")
            except Exception as e:
                with open('error.txt','w+') as f:
                    f.write(str(e)+','+dirname)

if  __name__ =="__main__":
    classify()
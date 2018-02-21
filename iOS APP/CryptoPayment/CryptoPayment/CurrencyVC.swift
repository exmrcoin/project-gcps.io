//
//  CurrencyVC.swift
//  CryptoPayment
//
//  Created by Joy on 19/02/18.
//  Copyright © 2018 Apple Inc. All rights reserved.
//

import UIKit

class CurrencyVC: UIViewController, UITableViewDelegate, UITableViewDataSource {
    
    // MARK: - Outlets
    // MARK: -

    @IBOutlet weak var btnClose: UIButton!
    @IBOutlet weak var tblCurrencyInput: UITableView!
    
    
    // MARK: - Properties
    // MARK: -
    
    var arrCurrencyVal : [[String : Any]] = [["Country":"USD",
                                              "Country_Val":"United States Dollar"],
                                             ["Country":"CAD",
                                              "Country_Val":"Canadian Dollar"],
                                             ["Country":"EUR",
                                              "Country_Val":"Euro"],
                                             ["Country":"AUD",
                                              "Country_Val":"Australian Dollar"]]
    
    
    // MARK: - VCCycles
    // MARK: -
    
    override func viewDidLoad() {
        super.viewDidLoad()
        self.tblCurrencyInput.delegate = self
        self.tblCurrencyInput.dataSource = self
//        self.tblCurrencyInput.reloadData()
        // Do any additional setup after loading the view.
    }
    
    override func viewWillAppear(_ animated: Bool) {
        super.viewWillAppear(true)
        self.btnClose.layer.cornerRadius = self.btnClose.frame.height/2
    }

    override func didReceiveMemoryWarning() {
        super.didReceiveMemoryWarning()
        // Dispose of any resources that can be recreated.
    }
    
    
    // MARK: - Btn Actions
    // MARK: -
    
    @IBAction func btnCloseAction(_ sender: UIButton) {
        
        let MainStry = UIStoryboard(name: Constant.Storyboard.kMain, bundle: nil)
        let InviteVC = MainStry.instantiateViewController(withIdentifier: Constant.ViewControllerID.kHomeVC) as! HomeVC
        self.navigationController?.pushViewController(InviteVC, animated: true)
        
    }
    
    
    
    @IBAction func btnBackAction(_ sender: UIButton) {
        
        self.navigationController?.popViewController(animated: true)
        
    }
    
    
    @IBAction func btnCurrencyTapped(_ sender: UIButton) {
        
        if sender.currentImage == UIImage(named:"uncheck"){
            
            sender.setImage(UIImage(named:"checked"), for: .normal)
            
        }else{
            sender.setImage(UIImage(named:"uncheck"), for: .normal)
        }
        
    }
    
    
    // MARK: - Table Delegates
    // MARK: -
    
    func tableView(_ tableView: UITableView, numberOfRowsInSection section: Int) -> Int {
        return arrCurrencyVal.count
    }
    
    func tableView(_ tableView: UITableView, cellForRowAt indexPath: IndexPath) -> UITableViewCell {
        let currencyCell = tableView.dequeueReusableCell(withIdentifier: "CurrencyCell") as! TblCurrencyCell
        
        let aDictData = self.arrCurrencyVal[indexPath.row] as [String:Any]
        currencyCell.lblCurrencyName.text = aDictData["Country"] as? String
        currencyCell.lblCurrencyVal.text = aDictData["Country_Val"] as? String
        
        return currencyCell
    }
    
    func tableView(_ tableView: UITableView, didSelectRowAt indexPath: IndexPath) {
        
        
        
    }

    /*
    // MARK: - Navigation

    // In a storyboard-based application, you will often want to do a little preparation before navigation
    override func prepare(for segue: UIStoryboardSegue, sender: Any?) {
        // Get the new view controller using segue.destinationViewController.
        // Pass the selected object to the new view controller.
    }
    */

}

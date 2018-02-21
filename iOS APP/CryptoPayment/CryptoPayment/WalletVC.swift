//
//  WalletVC.swift
//  CryptoPayment
//
//  Created by Joy on 20/02/18.
//  Copyright © 2018 Apple Inc. All rights reserved.
//

import UIKit

class WalletVC: UIViewController , UITableViewDataSource, UITableViewDelegate{
    
    // MARK: - Outlets
    // MARK: -
    
    @IBOutlet weak var lblPrice: UILabel!
    @IBOutlet weak var btnAdd: UIButton!
    @IBOutlet weak var tblWalletVal: UITableView!
    
    // MARK: - Properties
    // MARK: -
    
    var arrWalletVal : [[String : Any]] = [["Wallet_name":"BTC",
                                            "Wallet_price":"0.000",
                                              "Wallet_img":"bit_coin_Dark"],
                                           ["Wallet_name":"LTC",
                                            "Wallet_price":"0.000",
                                            "Wallet_img":"ltc"],
                                           ["Wallet_name":"XRP",
                                            "Wallet_price":"0.000",
                                            "Wallet_img":"ripple"]]
    
    // MARK: - VCCycles
    // MARK: -
    
    override func viewDidLoad() {
        super.viewDidLoad()
        self.tblWalletVal.delegate = self
        self.tblWalletVal.dataSource = self
        // Do any additional setup after loading the view.
    }
    
    override func viewWillAppear(_ animated: Bool) {
        super.viewWillAppear(true)
        let boldText  = "$ "
        
        let attrs = [NSFontAttributeName: UIFont(name: "Avenir Light", size: 18.0)!]
        let attributedString = NSMutableAttributedString(string:boldText, attributes:attrs)
//        let attrVal =
        let normalText = "200"
        let normalString = NSMutableAttributedString(string:normalText)
        
        let pointVal = ".00"
        let attritedString = NSMutableAttributedString(string:pointVal, attributes:attrs)
        
        attributedString.append(normalString)
        attributedString.append(attritedString)
        lblPrice.attributedText = attributedString
        self.btnAdd.layer.cornerRadius = self.btnAdd.frame.height/2
    }

    override func didReceiveMemoryWarning() {
        super.didReceiveMemoryWarning()
        // Dispose of any resources that can be recreated.
    }
    
    // MARK: - BtnActions
    // MARK: -
    
    @IBAction func btnValShuffle(_ sender: UIButton) {
    }
    @IBAction func btnBackAction(_ sender: UIButton) {
        
        self.navigationController?.popViewController(animated: true)
        
    }
    @IBAction func btnAddAction(_ sender: UIButton) {
    }

    @IBAction func btnRecieveActionVal(_ sender: UIButton) {
        
        let MainStry = UIStoryboard(name: Constant.Storyboard.kMain, bundle: nil)
        let PasscodeVC = MainStry.instantiateViewController(withIdentifier: Constant.ViewControllerID.kRecieverVC) as! RecieveVC
        self.navigationController?.pushViewController(PasscodeVC, animated: true)
        
    }
    @IBAction func btnSendActionVal(_ sender: UIButton) {
        
        let MainStry = UIStoryboard(name: Constant.Storyboard.kMain, bundle: nil)
        let PasscodeVC = MainStry.instantiateViewController(withIdentifier: Constant.ViewControllerID.kSendVC) as! SendVC
        self.navigationController?.pushViewController(PasscodeVC, animated: true)
        
    }
    
    @IBAction func btnConvertActionVal(_ sender: UIButton) {
        
        let MainStry = UIStoryboard(name: Constant.Storyboard.kMain, bundle: nil)
        let PasscodeVC = MainStry.instantiateViewController(withIdentifier: Constant.ViewControllerID.kConvertVC) as! ConvertVC
        self.navigationController?.pushViewController(PasscodeVC, animated: true)
        
    }
    
    // MARK: - Table Delegates
    // MARK: -
    
    func tableView(_ tableView: UITableView, numberOfRowsInSection section: Int) -> Int {
        return arrWalletVal.count
    }
    
    func tableView(_ tableView: UITableView, cellForRowAt indexPath: IndexPath) -> UITableViewCell {
        let currencyCell = tableView.dequeueReusableCell(withIdentifier: "WalletCell") as! WalletCell
        
        let aDictData = arrWalletVal[indexPath.row] as [String:Any]
        currencyCell.lblWalletName.text = aDictData["Wallet_name"] as? String
        currencyCell.lblWalletPrice.text = aDictData["Wallet_price"] as? String
        let imgName = aDictData["Wallet_img"] as? String
        currencyCell.ivWallet.image = UIImage(named : imgName!)
        
        return currencyCell
    }
    
    func tableView(_ tableView: UITableView, didSelectRowAt indexPath: IndexPath) {
        if indexPath.row == 0{
            //            let productListVC = self.storyboard?.instantiateViewController(withIdentifier: Constant.ViewControllerID.kProductListVC) as! ProductListVC
            //            productListVC.strNavTitle = "Offer"
            //            self.navigationController?.pushViewController(productListVC, animated: true)
        }
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

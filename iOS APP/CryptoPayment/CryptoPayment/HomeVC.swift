//
//  HomeVC.swift
//  CryptoPayment
//
//  Created by Joy on 19/02/18.
//  Copyright © 2018 Apple Inc. All rights reserved.
//

import UIKit

class HomeVC: UIViewController {

    @IBOutlet weak var btnWallet: UIButton!
    @IBOutlet weak var btnPOS: UIButton!
    @IBOutlet weak var btnHome: UIButton!
    @IBOutlet weak var btnHistory: UIButton!
    @IBOutlet weak var btnSetting: UIButton!
    @IBOutlet weak var lblShareRate: UILabel!
    @IBOutlet weak var lblTTLPrice: UILabel!
    
    
    override func viewDidLoad() {
        super.viewDidLoad()

        // Do any additional setup after loading the view.
    }

    override func didReceiveMemoryWarning() {
        super.didReceiveMemoryWarning()
        // Dispose of any resources that can be recreated.
    }
    
    @IBAction func btnWalletAction(_ sender: UIButton) {
        
        let MainStry = UIStoryboard(name: Constant.Storyboard.kMain, bundle: nil)
        let InviteVC = MainStry.instantiateViewController(withIdentifier: Constant.ViewControllerID.kWalletVC) as! WalletVC
        self.navigationController?.pushViewController(InviteVC, animated: true)
        
    }
    @IBAction func btnPOSAction(_ sender: UIButton) {
        
        
        
        
    }
    @IBAction func btnHomeAction(_ sender: UIButton) {
        
        
        
    }
    @IBAction func btnHistoryAction(_ sender: UIButton) {
        
        
        
    }
    @IBAction func btnSettingAction(_ sender: UIButton) {
        
        let MainStry = UIStoryboard(name: Constant.Storyboard.kMain, bundle: nil)
        let InviteVC = MainStry.instantiateViewController(withIdentifier: Constant.ViewControllerID.kSettingVC) as! SettingVC
        self.navigationController?.pushViewController(InviteVC, animated: true)
        
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

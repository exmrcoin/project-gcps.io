//
//  RecieveVC.swift
//  CryptoPayment
//
//  Created by Joy on 20/02/18.
//  Copyright © 2018 Apple Inc. All rights reserved.
//

import UIKit

class RecieveVC: UIViewController {
    
    // MARK: - Outlets
    // MARK: -
    
    @IBOutlet weak var lblNavTitle: UILabel!
    @IBOutlet weak var btnTapToCopy: UIButton!
    @IBOutlet weak var btnShareAdd: UIButton!
    @IBOutlet weak var ivQrCode: UIImageView!
    @IBOutlet weak var lblQrCodeVal: UILabel!
    
    @IBOutlet weak var ivRecieve: UIImageView!
    @IBOutlet weak var lblRecieve: UILabel!
    
    // MARK: - VCCycles
    // MARK: -

    override func viewDidLoad() {
        super.viewDidLoad()

        // Do any additional setup after loading the view.
    }
    
    override func viewWillAppear(_ animated: Bool) {
        super.viewWillAppear(true)
        self.ivRecieve.image = UIImage(named:"receive_orange")
        self.lblRecieve.textColor = UIColor.init(red: 230.0/255.0, green: 90.0/255.0, blue: 20.0/255.0, alpha: 1.0)
        self.btnTapToCopy.layer.cornerRadius = self.btnTapToCopy.frame.height/2
        self.btnShareAdd.layer.cornerRadius = self.btnShareAdd.frame.height/2
    }
    

    override func didReceiveMemoryWarning() {
        super.didReceiveMemoryWarning()
        // Dispose of any resources that can be recreated.
    }
    
    // MARK: - BtnActions
    // MARK: -
    
    @IBAction func btnShareAddress(_ sender: UIButton) {
    }
    @IBAction func btnCopyAction(_ sender: UIButton) {
    }
    @IBAction func btnBackAction(_ sender: UIButton) {
        
        for vc in (self.navigationController?.viewControllers ?? []) {
            if vc is WalletVC {
                _ = self.navigationController?.popToViewController(vc, animated: true)
                vc.reloadInputViews()
                break
            }
        }
        
    }
    
    @IBAction func btnRecieveActionVal(_ sender: UIButton) {
        
        
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
    
    /*
    // MARK: - Navigation

    // In a storyboard-based application, you will often want to do a little preparation before navigation
    override func prepare(for segue: UIStoryboardSegue, sender: Any?) {
        // Get the new view controller using segue.destinationViewController.
        // Pass the selected object to the new view controller.
    }
    */

}

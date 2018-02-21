//
//  SendVC.swift
//  CryptoPayment
//
//  Created by Joy on 20/02/18.
//  Copyright © 2018 Apple Inc. All rights reserved.
//

import UIKit

class SendVC: UIViewController {
    
    // MARK: - Outlets
    // MARK: -

    @IBOutlet weak var lblFrom: UILabel!
    @IBOutlet weak var lblFromVal: UILabel!
    @IBOutlet weak var lblTo: UILabel!
    @IBOutlet weak var lblAmount: UILabel!
    @IBOutlet weak var lblValue: UILabel!
    @IBOutlet weak var tfToVal: UITextField!
    @IBOutlet weak var tfAmtVal: UITextField!
    @IBOutlet weak var tfValueVal: UITextField!
    @IBOutlet weak var btnSend: UIButton!
    
    @IBOutlet weak var ivSend: UIImageView!
    @IBOutlet weak var lblSend: UILabel!
    // MARK: - VCCycles
    // MARK: -
    
    override func viewDidLoad() {
        super.viewDidLoad()

        // Do any additional setup after loading the view.
    }
    
    
    override func viewWillAppear(_ animated: Bool) {
        super.viewWillAppear(true)
        self.ivSend.image = UIImage(named:"send_orange")
        self.lblSend.textColor = UIColor.init(red: 230.0/255.0, green: 90.0/255.0, blue: 20.0/255.0, alpha: 1.0)
        self.btnSend.layer.cornerRadius = self.btnSend.frame.height/2
    }

    override func didReceiveMemoryWarning() {
        super.didReceiveMemoryWarning()
        // Dispose of any resources that can be recreated.
    }
    
    // MARK: - Button Actions
    // MARK: -
    
    @IBAction func btnBackAction(_ sender: UIButton) {
        
        for vc in (self.navigationController?.viewControllers ?? []) {
            if vc is WalletVC {
                _ = self.navigationController?.popToViewController(vc, animated: true)
                vc.reloadInputViews()
                break
            }
        }
        
    }
    @IBAction func btnSendValue(_ sender: UIButton) {
    }
    
    @IBAction func btnRecieveActionVal(_ sender: UIButton) {
        
        let MainStry = UIStoryboard(name: Constant.Storyboard.kMain, bundle: nil)
        let PasscodeVC = MainStry.instantiateViewController(withIdentifier: Constant.ViewControllerID.kRecieverVC) as! RecieveVC
        self.navigationController?.pushViewController(PasscodeVC, animated: true)
        
    }
    @IBAction func btnSendActionVal(_ sender: UIButton) {
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

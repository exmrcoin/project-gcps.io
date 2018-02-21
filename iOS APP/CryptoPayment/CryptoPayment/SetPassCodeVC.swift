//
//  SetPassCodeVC.swift
//  CryptoPayment
//
//  Created by Joy on 19/02/18.
//  Copyright © 2018 Apple Inc. All rights reserved.
//

import UIKit

class SetPassCodeVC: UIViewController {
    
    // MARK: - Outlets
    // MARK: -
    
    @IBOutlet var tfCode1: UITextField!
    @IBOutlet var tfCode2: UITextField!
    @IBOutlet var tfCode3: UITextField!
    @IBOutlet var tfCode4: UITextField!
    
    @IBOutlet var btnPad1: UIButton!
    @IBOutlet var btnPad2: UIButton!
    @IBOutlet var btnPad3: UIButton!
    @IBOutlet var btnPad4: UIButton!
    @IBOutlet var btnPad5: UIButton!
    @IBOutlet var btnPad6: UIButton!
    @IBOutlet var btnPad7: UIButton!
    @IBOutlet var btnPad8: UIButton!
    @IBOutlet var btnPad9: UIButton!
    @IBOutlet var btnPad0: UIButton!
    @IBOutlet weak var btnPadDot: UIButton!
    @IBOutlet weak var btnClear: UIButton!
    
    // MARK: - Properties
    // MARK: -
    
    var tfWorking : UITextField!
    var email_id : String!
    var frstTfVal : String!
    var SecTfVal : String!
    var thrdTfVal : String!
    var fourthTFVal : String!
    // MARK: - VCCycles
    // MARK: -
    
    override func viewDidLoad() {
        super.viewDidLoad()
        tfWorking = tfCode1
        // Do any additional setup after loading the view.
    }

    override func didReceiveMemoryWarning() {
        super.didReceiveMemoryWarning()
        // Dispose of any resources that can be recreated.
    }
    
    override func viewWillAppear(_ animated: Bool) {
        super.viewWillAppear(true)
        tfCode1.text = ""
        tfCode2.text = ""
        tfCode3.text = ""
        tfCode4.text = ""
        tfWorking.text = ""
        tfWorking = tfCode1
    }
    
    // MARK: - Btn Actions
    // MARK: -
    
    @IBAction func btnBackAction(_ sender: UIButton) {
        
        self.navigationController?.popViewController(animated: true)
        
    }

    
    @IBAction func btn1(_ sender: Any) {
        self.textMethod("1")
    }
    
    @IBAction func btn2(_ sender: Any) {
        self.textMethod("2")
    }
    
    @IBAction func btn3(_ sender: Any) {
        self.textMethod("3")
    }
    
    @IBAction func btn4(_ sender: Any) {
        self.textMethod("4")
    }
    
    @IBAction func btn6(_ sender: Any) {
        self.textMethod("6")
    }
    
    @IBAction func btn5(_ sender: Any) {
        self.textMethod("5")
    }
    
    @IBAction func btn7(_ sender: Any) {
        self.textMethod("7")
    }
    
    @IBAction func btn8(_ sender: Any) {
        self.textMethod("8")
    }
    
    @IBAction func btn9(_ sender: Any) {
        self.textMethod("9")
    }
    
    @IBAction func btn0(_ sender: Any) {
        self.textMethod("0")
    }
    
    @IBAction func btnX(_ sender: Any) {
        self.textMethod("X")
    }
    @IBAction func btnDot(_ sender: Any) {
        self.textMethod(".")
        
    }
    
    // MARK: - Methods
    // MARK: -
    
    func textMethod(_ text : String)  {
        if tfWorking == nil {
            return
        }
        else{
            
            if text == "X"{
                tfWorking.text = ""
                self.backwardMove()
            }
            else{
                tfWorking.text = text
                self.forwardMove()
            }
        }
    }
    
    func forwardMove()  {
        if tfWorking == tfCode1{
            tfWorking = tfCode2
        }
        else if tfWorking == tfCode2{
            tfWorking = tfCode3
        }
        else if tfWorking == tfCode3{
            tfWorking = tfCode4
        }
        else if tfWorking == tfCode4{
            
            if((tfCode1.text! == frstTfVal)&&(tfCode2.text! == SecTfVal)&&(tfCode3.text! == thrdTfVal)&&(tfCode4.text! == fourthTFVal)){
                let PasscodeVal = UserDefaults.standard
                PasscodeVal.set(tfCode1.text!, forKey: "frstVal")
                PasscodeVal.set(tfCode2.text!, forKey: "SecVal")
                PasscodeVal.set(tfCode3.text!, forKey: "ThrdVal")
                PasscodeVal.set(tfCode4.text!, forKey: "FourthVal")
                PasscodeVal.synchronize()
                for vc in (self.navigationController?.viewControllers ?? []) {
                    if vc is SettingVC {
                        _ = self.navigationController?.popToViewController(vc, animated: true)
                        vc.reloadInputViews()
                        break
                    }
                }
            }else{
                Alert.showAlert(self, title: "Error", message: "Code are mismatching")
            }
        }
    }
    
    func backwardMove()  {
        if tfWorking == tfCode4{
            tfWorking = tfCode3
        }
        else if tfWorking == tfCode3{
            tfWorking = tfCode2
        }
        else if tfWorking == tfCode2{
            tfWorking = tfCode1
        }
        else if tfWorking == tfCode1{
            
            
            
            // Nothing
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

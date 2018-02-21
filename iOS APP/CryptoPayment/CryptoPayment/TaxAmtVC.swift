//
//  TaxAmtVC.swift
//  CryptoPayment
//
//  Created by Joy on 20/02/18.
//  Copyright © 2018 Apple Inc. All rights reserved.
//

import UIKit

class TaxAmtVC: UIViewController {

    @IBOutlet weak var btnApply: UIButton!
    @IBOutlet weak var lblTaxRate: UILabel!
    @IBOutlet weak var vwTaxView: UIView!
    
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
    
    
    
    override func viewDidLoad() {
        super.viewDidLoad()

        // Do any additional setup after loading the view.
    }
    
    override func viewWillAppear(_ animated: Bool) {
        super.viewWillAppear(true)
        
        self.btnApply.layer.cornerRadius = self.btnApply.frame.height/2
        self.vwTaxView.layer.cornerRadius = self.vwTaxView.frame.height/2
        
    }

    override func didReceiveMemoryWarning() {
        super.didReceiveMemoryWarning()
        // Dispose of any resources that can be recreated.
    }
    
    @IBAction func btn1(_ sender: Any) {
        
    }
    
    @IBAction func btn2(_ sender: Any) {
        
    }
    
    @IBAction func btn3(_ sender: Any) {
        
    }
    
    @IBAction func btn4(_ sender: Any) {
        
    }
    
    @IBAction func btn6(_ sender: Any) {
        
    }
    
    @IBAction func btn5(_ sender: Any) {
        
    }
    
    @IBAction func btn7(_ sender: Any) {
        
    }
    
    @IBAction func btn8(_ sender: Any) {
        
    }
    
    @IBAction func btn9(_ sender: Any) {
        
    }
    
    @IBAction func btn0(_ sender: Any) {
        
    }
    
    @IBAction func btnX(_ sender: Any) {
        
    }
    @IBAction func btnDot(_ sender: Any) {
        
        
    }
    
    
    @IBAction func btnBackAction(_ sender: UIButton) {
        
        self.navigationController?.popViewController(animated: true)
        
    }
    @IBAction func btnApplyAction(_ sender: UIButton) {
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

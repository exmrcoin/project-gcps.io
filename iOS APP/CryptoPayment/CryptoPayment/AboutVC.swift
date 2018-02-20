//
//  AboutVC.swift
//  CryptoPayment
//
//  Created by Joy on 19/02/18.
//  Copyright © 2018 Apple Inc. All rights reserved.
//

import UIKit

class AboutVC: UIViewController {
    
    // MARK: - Outlets
    // MARK: -
    
    // MARK: - Properties
    // MARK: -
    
    // MARK: - VCCycles
    // MARK: -

    override func viewDidLoad() {
        super.viewDidLoad()

        // Do any additional setup after loading the view.
    }

    override func didReceiveMemoryWarning() {
        super.didReceiveMemoryWarning()
        // Dispose of any resources that can be recreated.
    }
    
    // MARK: - Btn Actions
    // MARK: -
    
    @IBAction func btnBackAction(_ sender: UIButton) {
        
        self.navigationController?.popViewController(animated: true)
        
    }

}

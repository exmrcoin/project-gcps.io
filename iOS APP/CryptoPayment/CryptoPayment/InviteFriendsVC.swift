//
//  InviteFriendsVC.swift
//  CryptoPayment
//
//  Created by Joy on 19/02/18.
//  Copyright © 2018 Apple Inc. All rights reserved.
//

import UIKit

class InviteFriendsVC: UIViewController {
    
    
    // MARK: - Outlets
    // MARK: -

    @IBOutlet weak var btnInviteFrnds: UIButton!
    
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
    
    override func viewWillAppear(_ animated: Bool) {
        super.viewWillAppear(true)
        self.btnInviteFrnds.layer.cornerRadius = self.btnInviteFrnds.frame.height/2
    }
    
    
    // MARK: - Btn Actions
    // MARK: -
    
    @IBAction func btnBackAction(_ sender: UIButton) {
        
        self.navigationController?.popViewController(animated: true)
        
    }
    
    @IBAction func btnInviteAction(_ sender: UIButton) {
        
        
        
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

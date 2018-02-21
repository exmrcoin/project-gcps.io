//
//  ViewController.swift
//  CryptoPayment
//
//  Created by Joy on 19/02/18.
//  Copyright © 2018 Apple Inc. All rights reserved.
//

import UIKit

class LoginVC: UIViewController {

    // MARK: - Outlets
    // MARK: -
    
    @IBOutlet weak var btnScanLogin: UIButton!
    
    // MARK: - Properties
    // MARK: -
    
    // MARK: - VCCycles
    // MARK: -
    
    override func viewDidLoad() {
        super.viewDidLoad()
        // Do any additional setup after loading the view, typically from a nib.
    }
    
    override func viewWillAppear(_ animated: Bool) {
        super.viewWillAppear(true)
        self.btnScanLogin.layer.cornerRadius = self.btnScanLogin.frame.height/2
    }

    override func didReceiveMemoryWarning() {
        super.didReceiveMemoryWarning()
        // Dispose of any resources that can be recreated.
    }
    
    // MARK: - Btn Action
    // MARK: -
    
    @IBAction func btnLoginAction(_ sender: UIButton) {
//        QRScannerVC
        let MainStry = UIStoryboard(name: Constant.Storyboard.kMain, bundle: nil)
        let PasscodeVC = MainStry.instantiateViewController(withIdentifier: Constant.ViewControllerID.kQRScannerVC) as! QRScannerVC
        
        self.navigationController?.pushViewController(PasscodeVC, animated: true)        
    }
    
    // MARK: - Methods
    // MARK: -
    
//    func showQRCodeScanner() {
//        let scanner = CarQRCodeScannerController()
//        scanner.scannerDelegate = self
//        self.presentViewController(scanner, animated: true, completion: nil)
//    }
    


}

//extension LoginVC: CarQRCodeScannerControllerDelegate {
//    
//    func qrScannerControllerDidCancel(scanner: CarQRCodeScannerController) {
//        print("canceld!")
//    }
//    
//    func qrScannerController(scanner: CarQRCodeScannerController, didFinishScanning certificate: CarInspectionCertificate) {
//        print(certificate)
//    }
//    
//}


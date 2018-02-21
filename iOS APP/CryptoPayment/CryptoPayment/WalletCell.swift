//
//  WalletCell.swift
//  CryptoPayment
//
//  Created by Joy on 20/02/18.
//  Copyright © 2018 Apple Inc. All rights reserved.
//

import UIKit

class WalletCell: UITableViewCell {
    @IBOutlet weak var lblWalletName: UILabel!
    @IBOutlet weak var ivWallet: UIImageView!
    @IBOutlet weak var lblWalletPrice: UILabel!
    
    override func awakeFromNib() {
        super.awakeFromNib()
        // Initialization code
    }

    override func setSelected(_ selected: Bool, animated: Bool) {
        super.setSelected(selected, animated: animated)

        // Configure the view for the selected state
    }

}
